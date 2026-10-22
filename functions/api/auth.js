// Login do painel no Cloudflare Pages. Variáveis: GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
export async function onRequestGet({ request, env }) {
  if (!env.GITHUB_CLIENT_ID || !env.GITHUB_CLIENT_SECRET)
    return new Response("Painel ainda sem as chaves do GitHub: cadastre GITHUB_CLIENT_ID e GITHUB_CLIENT_SECRET na hospedagem e publique de novo.", { status: 500, headers: { "Content-Type": "text/plain; charset=utf-8" } });
  const url = new URL(request.url);
  const state = crypto.randomUUID().replace(/-/g, "");
  const gh = new URL("https://github.com/login/oauth/authorize");
  gh.search = new URLSearchParams({ client_id: env.GITHUB_CLIENT_ID, scope: "repo,user", state, redirect_uri: `${url.origin}/api/callback` });
  return new Response(null, { status: 302, headers: {
    Location: gh.toString(), "Cache-Control": "no-store",
    "Set-Cookie": `decap_state=${state}; Path=/api/; Max-Age=600; Secure; HttpOnly; SameSite=Lax` } });
}
