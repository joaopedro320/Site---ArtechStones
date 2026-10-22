// Login do painel na Vercel. Variáveis: GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
export async function GET(request) {
  const env = process.env;
  const url = new URL(request.url);
  const state = crypto.randomUUID().replace(/-/g, "");
  const gh = new URL("https://github.com/login/oauth/authorize");
  gh.search = new URLSearchParams({ client_id: env.GITHUB_CLIENT_ID, scope: "repo,user", state, redirect_uri: `${url.origin}/api/callback` });
  return new Response(null, { status: 302, headers: {
    Location: gh.toString(), "Cache-Control": "no-store",
    "Set-Cookie": `decap_state=${state}; Path=/api/; Max-Age=600; Secure; HttpOnly; SameSite=Lax` } });
}
