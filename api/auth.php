<?php
// Login do painel (Hostinger). Credenciais ficam FORA da pasta pública, em ../decap-oauth.php
$cfgFile = dirname($_SERVER['DOCUMENT_ROOT']) . '/decap-oauth.php';
if (!is_file($cfgFile)) { http_response_code(500); exit('Painel ainda nao configurado (falta decap-oauth.php).'); }
$cfg = require $cfgFile;
$state = bin2hex(random_bytes(16));
setcookie('decap_state', $state, ['expires' => time() + 600, 'path' => '/api/', 'secure' => true, 'httponly' => true, 'samesite' => 'Lax']);
header('Cache-Control: no-store');
header('Location: https://github.com/login/oauth/authorize?' . http_build_query([
  'client_id' => $cfg['client_id'], 'scope' => 'repo,user', 'state' => $state,
  'redirect_uri' => 'https://' . $_SERVER['HTTP_HOST'] . '/api/callback',
]));
