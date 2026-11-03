// api/clerk-proxy/[...path].js — Proxy de Clerk para Vercel (modo production).
//
// El navegador llama a https://<app>/__clerk/* (ver vercel.json, rewrite
// /__clerk/(.*) -> /api/clerk-proxy/$1) y esta función reenvía la petición a la
// Frontend API de Clerk (https://frontend-api.clerk.dev) con las cabeceras que
// exige el modo proxy documentado por Clerk:
//   - Clerk-Proxy-Url: origen público del proxy (atribuye la instancia)
//   - Clerk-Secret-Key: clave secreta del servidor (nunca llega al navegador)
//   - X-Forwarded-For: IP real del cliente
// Las respuestas se devuelven tal cual, reescribiendo Location si apunta al
// dominio de Clerk para que el navegador vuelva a entrar por el proxy.

const FAPI_ORIGIN = 'https://frontend-api.clerk.dev';
const INSTANCE_ORIGIN = 'https://clerk.planificador-itinerarios.vercel.app';
const PROXY_PATH = '/__clerk';
const ROUTE_PREFIX = '/api/clerk-proxy';

// Cabeceras hop-by-hop o gestionadas por fetch: no se reenvían tal cual.
const SKIP_REQUEST_HEADERS = new Set([
  'connection',
  'keep-alive',
  'transfer-encoding',
  'upgrade',
  'host',
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

function collectBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', (chunk) => chunks.push(chunk));
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

function rewriteLocation(location, proxyUrl) {
  if (location.startsWith(FAPI_ORIGIN)) {
    return proxyUrl + location.slice(FAPI_ORIGIN.length);
  }
  if (location.startsWith(INSTANCE_ORIGIN)) {
    return proxyUrl + location.slice(INSTANCE_ORIGIN.length);
  }
  return location;
}

module.exports = async function clerkProxyHandler(req, res) {
  try {
    const secretKey = process.env.CLERK_SECRET_KEY || '';
    if (!secretKey) {
      res.statusCode = 500;
      res.setHeader('content-type', 'application/json');
      res.end(JSON.stringify({ error: 'CLERK_SECRET_KEY no está configurada.' }));
      return;
    }

    const host =
      req.headers['x-forwarded-host'] ||
      req.headers.host ||
      'planificador-itinerarios.vercel.app';
    const proto = req.headers['x-forwarded-proto'] || 'https';
    const proxyUrl = `${proto}://${host}${PROXY_PATH}`;

    // /api/clerk-proxy/v1/foo?x=1  ->  /v1/foo?x=1
    const rest = req.url.startsWith(ROUTE_PREFIX)
      ? req.url.slice(ROUTE_PREFIX.length)
      : req.url;
    const target = `${FAPI_ORIGIN}${rest.startsWith('/') ? rest : `/${rest}`}`;

    const headers = {};
    for (const [name, value] of Object.entries(req.headers)) {
      const key = name.toLowerCase();
      if (!SKIP_REQUEST_HEADERS.has(key) && value !== undefined) {
        headers[key] = value;
      }
    }
    headers.host = 'frontend-api.clerk.dev';
    headers['clerk-proxy-url'] = proxyUrl;
    headers['clerk-secret-key'] = secretKey;
    if (req.headers['x-forwarded-for']) {
      headers['x-forwarded-for'] = req.headers['x-forwarded-for'];
    }

    const method = (req.method || 'GET').toUpperCase();
    const body =
      method === 'GET' || method === 'HEAD'
        ? undefined
        : await collectBody(req);

    const upstream = await fetch(target, {
      method,
      headers,
      body,
      redirect: 'manual',
    });

    const responseHeaders = {};
    upstream.headers.forEach((value, name) => {
      const key = name.toLowerCase();
      if (!SKIP_RESPONSE_HEADERS.has(key)) {
        responseHeaders[key] = value;
      }
    });
    const setCookies = upstream.headers.getSetCookie
      ? upstream.headers.getSetCookie()
      : [];
    if (setCookies.length > 0) {
      responseHeaders['set-cookie'] = setCookies;
    }

    const location = upstream.headers.get('location');
    if (location) {
      responseHeaders.location = rewriteLocation(location, proxyUrl);
    }

    const payload = Buffer.from(await upstream.arrayBuffer());
    res.statusCode = upstream.status;
    for (const [name, value] of Object.entries(responseHeaders)) {
      res.setHeader(name, value);
    }
    res.setHeader('content-length', String(payload.length));
    res.end(payload);
  } catch (error) {
    console.error('clerk-proxy error:', error);
    if (!res.headersSent) {
      res.statusCode = 502;
      res.setHeader('content-type', 'application/json');
      res.end(JSON.stringify({ error: 'No se pudo contactar con Clerk.' }));
    } else {
      res.end();
    }
  }
};
