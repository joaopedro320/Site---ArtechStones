<?php
// Retorno do GitHub: troca o código pelo token e entrega ao painel (só para a mesma origem).
$cfgFile = dirname($_SERVER['DOCUMENT_ROOT']) . '/decap-oauth.php';
if (!is_file($cfgFile)) { http_response_code(500); exit('Painel ainda nao configurado.'); }
$cfg = require $cfgFile;
header('Cache-Control: no-store');
$origin = 'https://' . $_SERVER['HTTP_HOST'];
$ok = isset($_GET['code'], $_GET['state'], $_COOKIE['decap_state']) && hash_equals($_COOKIE['decap_state'], $_GET['state']);
setcookie('decap_state', '', ['expires' => 1, 'path' => '/api/', 'secure' => true, 'httponly' => true, 'samesite' => 'Lax']);
$msg = 'error'; $content = ['error' => 'Falha no login'];
if ($ok) {
  $ctx = stream_context_create(['http' => ['method' => 'POST', 'timeout' => 15,
    'header' => "Accept: application/json\r\nContent-Type: application/x-www-form-urlencoded\r\nUser-Agent: artechstone-admin\r\n",
    'content' => http_build_query(['client_id' => $cfg['client_id'], 'client_secret' => $cfg['client_secret'], 'code' => $_GET['code']])]]);
  $res = json_decode((string) @file_get_contents('https://github.com/login/oauth/access_token', false, $ctx), true);
  if (!empty($res['access_token'])) { $msg = 'success'; $content = ['token' => $res['access_token'], 'provider' => 'github']; }
}
$payload = json_encode('authorization:github:' . $msg . ':' . json_encode($content));
$o = json_encode($origin);
echo "<!doctype html><meta charset=utf-8><title>Login</title><script>
(function(){var O=$o;function r(e){if(e.origin!==O)return;window.opener.postMessage($payload,O);window.removeEventListener('message',r);}
window.addEventListener('message',r);window.opener.postMessage('authorizing:github',O);})();
</script>";
