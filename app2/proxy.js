// app2/proxy.js — Routing Middleware de Vercel: proxy de Clerk en /__clerk.
//
// El navegador llama a https://<app>/__clerk/* y este middleware reenvía la
// petición a la Frontend API de Clerk (https://frontend-api.clerk.dev) con las
// cabeceras que exige el modo proxy de Clerk:
//   - Clerk-Proxy-Url: origen público del proxy (atribuye la instancia)
//   - Clerk-Secret-Key: clave secreta del servidor (nunca llega al navegador)
// El matcher en vercel.json limita la ejecución a /__clerk/*; el resto de
// peticiones siguen su curso normal (SPA / funciones / estáticos).

const FAPI_ORIGIN = 'https://frontend-api.clerk.dev';
const INSTANCE_ORIGIN = 'https://clerk.planificador-itinerarios.vercel.app';
const PROXY_PATH = '/__clerk';

// Cabeceras hop-by-hop o gestionadas por fetch: no se reenvían tal cual.
const SKIP_REQUEST_HEADERS = new Set([
  'host',
  'connection',
  'keep-alive',
  'transfer-encoding',
  'upgrade',
  'proxy-authenticate',
  'proxy-authorization',
  'te',
  'trailer',
  'content-length',
]);
const SKIP_RESPONSE_HEADERS = new Set([
  ...SKIP_REQUEST_HEADERS,
  'content-encoding', // fetch ya ha descomprimido el cuerpo
]);

function rewriteLocation(location, proxyUrl) {
  if (location.startsWith(FAPI_ORIGIN)) {
    return proxyUrl + location.slice(FAPI_ORIGIN.length);
  }
  if (location.startsWith(INSTANCE_ORIGIN)) {
    return proxyUrl + location.slice(INSTANCE_ORIGIN.length);
  }
  return location;
}

function errorResponse(status, message) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: { 'content-type': 'application/json' },
  });
}

export default async function proxy(request) {
  const incoming = new URL(request.url);
  // Si el matcher fallara y entra otra ruta, se continúa sin tocar nada.
  if (!incoming.pathname.startsWith(PROXY_PATH)) return;

  const secretKey = process.env.CLERK_SECRET_KEY;
  if (!secretKey) {
    return errorResponse(500, 'CLERK_SECRET_KEY no está configurada.');
  }

  const proxyUrl = `${incoming.origin}${PROXY_PATH}`;
  const rest = incoming.pathname.slice(PROXY_PATH.length) || '/';
  const target = `${FAPI_ORIGIN}${rest}${incoming.search}`;

  const headers = new Headers();
  request.headers.forEach((value, name) => {
    if (!SKIP_REQUEST_HEADERS.has(name.toLowerCase())) {
      headers.set(name, value);
    }
  });
  headers.set('host', 'frontend-api.clerk.dev');
  headers.set('clerk-proxy-url', proxyUrl);
  headers.set('clerk-secret-key', secretKey);

  const method = request.method.toUpperCase();
  const body =
    method === 'GET' || method === 'HEAD'
      ? undefined
      : await request.arrayBuffer();

  try {
    const upstream = await fetch(target, {
      method,
      headers,
      body,
      redirect: 'manual',
    });

    const responseHeaders = new Headers();
    upstream.headers.forEach((value, name) => {
      const key = name.toLowerCase();
      if (!SKIP_RESPONSE_HEADERS.has(key) && key !== 'set-cookie') {
        responseHeaders.set(name, value);
      }
    });
    const setCookies = upstream.headers.getSetCookie?.() ?? [];
    for (const cookie of setCookies) {
      responseHeaders.append('set-cookie', cookie);
    }
    const location = upstream.headers.get('location');
    if (location) {
      responseHeaders.set('location', rewriteLocation(location, proxyUrl));
    }

    return new Response(await upstream.arrayBuffer(), {
      status: upstream.status,
      statusText: upstream.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error('clerk-proxy error:', error);
    return errorResponse(502, 'No se pudo contactar con Clerk.');
  }
}
