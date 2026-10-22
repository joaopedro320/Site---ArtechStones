export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code"), state = url.searchParams.get("state");
  const cookie = (request.headers.get("Cookie") || "").match(/(?:^|;\s*)decap_state=([a-f0-9]+)/);
  let msg = "error", content = { error: "Falha no login" };
  if (code && state && cookie && cookie[1] === state) {
    const r = await fetch("https://github.com/login/oauth/access_token", {
      method: "POST", headers: { Accept: "application/json", "Content-Type": "application/json", "User-Agent": "artechstone-admin" },
      body: JSON.stringify({ client_id: env.GITHUB_CLIENT_ID, client_secret: env.GITHUB_CLIENT_SECRET, code }) });
    const j = await r.json().catch(() => ({}));
    if (j.access_token) { msg = "success"; content = { token: j.access_token, provider: "github" }; }
  }
  const O = JSON.stringify(url.origin), P = JSON.stringify(`authorization:github:${msg}:${JSON.stringify(content)}`);
  const html = `<!doctype html><meta charset=utf-8><title>Login</title><script>(function(){var O=${O};function r(e){if(e.origin!==O)return;window.opener.postMessage(${P},O);window.removeEventListener('message',r);}window.addEventListener('message',r);window.opener.postMessage('authorizing:github',O);})();</script>`;
  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store",
    "Set-Cookie": "decap_state=; Path=/api/; Max-Age=0; Secure; HttpOnly; SameSite=Lax" } });
}
