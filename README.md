# Site Artechstone (5 idiomas)

Site institucional + catálogo da Artechstone, feito pela QH4 Growth. Português (raiz), inglês, espanhol, chinês simplificado e japonês, cada idioma com URL própria, hreflang e conteúdo traduzido (não é tradução automática em tempo real).

## Estrutura

```
/                         Português (x-default)
/en/  /es/  /zh/  /ja/    demais idiomas
  pedras/ (stones/, piedras/)          catálogo com filtro e busca
  pedras/artechlaminas/                uma página por linha
  pedras/artechquartzo/
  pedras/artechnano/
  pedras/pedras-naturais/
  sobre/  garantia/  downloads/  perguntas-frequentes/  contato/
  obrigado/                            página de obrigado (noindex)
404.html                  página de erro em 5 idiomas
assets/css/site.css       estilos
assets/js/site.js         interações e animações
assets/js/vendor/         GSAP 3.13 (ScrollTrigger, SplitText) e Lenis 1.3, hospedados no próprio site
assets/img/               fotos em WebP (640, 1200 e 2000 px), favicons, logo
sitemap.xml               sitemap multilíngue com alternates e imagens
robots.txt                libera buscadores e robôs de IA, bloqueia /obrigado/
llms.txt, llms-full.txt   resumo e conteúdo completo para ChatGPT, Claude, Perplexity, Gemini
site.webmanifest
.htaccess                 Hostinger: HTTPS, 301 do site antigo, 404, cache e headers de segurança
_redirects, _headers      Cloudflare Pages: os mesmos 301, cache e headers
vercel.json               mesma configuração, caso um dia use Vercel
```

São 60 páginas (12 por idioma).

## Repositório e publicação

Repositório: https://github.com/joaopedro320/Site---ArtechStones

- Branch `main`: código fonte (o que se edita).
- Branch `deploy`: site pronto, gerado automaticamente pelo GitHub Actions a cada push na `main` (`.github/workflows/build.yml`). Não editar à mão.

O site funciona nas duas hospedagens sem mudar nada no código:

**Hostinger (QH4)**
1. hPanel > Avançado > Git: repositório `https://github.com/joaopedro320/Site---ArtechStones.git`, branch `deploy`, pasta `public_html` do domínio.
2. Ative o deploy automático (webhook) para atualizar a cada push. Como o repositório é privado, adicione a chave SSH que o hPanel mostra em GitHub > Settings > Deploy keys.
3. O `.htaccess` já cuida de HTTPS, redirecionamentos do site antigo, 404 e cache.

**Cloudflare Pages**
1. Workers & Pages > Create > Pages > Connect to Git > este repositório.
2. Branch de produção `main`, build command `pip install -r requirements.txt && python3 build.py`, output `dist`.
3. Cada branch ou pull request ganha uma prévia automática (é a prévia da revisão).

Nos dois casos: confira o domínio `artechstonebrasil.com.br`. Se for outro, troque `BASE` no `build.py` (canonical, hreflang, sitemap e schema usam esse domínio). Antes de trocar o DNS, copie os registros de e-mail (MX e TXT do Microsoft 365) para não derrubar o e-mail da Artechstone.

## Como editar pedras (Sold out, nova pedra, foto)

Cada pedra é um arquivo em `data/stones/` (ex.: `data/stones/calacatta-gold-laminas.json`).

- Marcar como esgotada: `"soldOut": true`
- Nova pedra: copie um arquivo, renomeie com o novo id e troque `id`, `name`, `line` (`laminas`, `quartzo`, `nano` ou `natural`) e `order`
- Foto: coloque a foto original (jpg, png ou webp, qualquer tamanho) em `data/stones/fotos/` e escreva o nome do arquivo em `"image"`. O build gera sozinho as versões WebP de 640, 1200 e 2000 px
- Acabamentos: `"finishes": ["Polido", "Acetinado"]`

Depois é só fazer commit na `main`: o GitHub Actions gera o site e atualiza a branch `deploy` sozinho. Para testar no computador: `pip install pillow` e `python3 build.py` (sai em `dist/`). Essa mesma estrutura é a que o painel de edição vai usar quando for aprovado: cada pedra em um arquivo facilita a revisão e o histórico.

Para pré-visualizar localmente com links relativos: `python3 build.py --preview` e abra `preview/index.html`.

## Pendências antes de publicar

- [ ] **E-mail.** O briefing veio com `relacoespublicas@contato@artechstonedobrasil.com.br.com.br` (endereço inválido). Usei `contato@artechstonedobrasil.com.br`, que está no site atual. Confirmar com a Stella.
- [ ] **GTM.** `GTM_ID` no `build.py` está como `GTM-XXXXXXX`. Enquanto for o placeholder, o script nem carrega.
- [ ] **Instagram da QH4** no rodapé: `instagram.com/qh4growth` (confirmar o @).
- [ ] **Stocklist.** As 36 pedras vieram do site atual (artechstonebrasil.com.br). Conferir com a stocklist da Stella e incluir mármores e quartzitos naturais, acabamentos e fotos de cada pedra.
- [ ] **Catálogo em PDF.** A página Downloads pede o catálogo pelo WhatsApp. Se houver PDF, dá para trocar por download direto.
- [ ] **Garantia completa.** A página traz só o que é fato hoje: garantia de 1 ano do ArtechNano e fabricação ISO 9000 (ArtechQuartzo e ArtechNano), ambos do site atual. Pedir à Stella os termos das outras linhas.
- [ ] **Divergência de dados:** o briefing diz que a Fabiane morou 27 anos em Singapura e, em outro trecho, 26 anos na Ásia. Usei 27 (história) e evitei repetir o número. O briefing escreve "Colin B. Thomas" e o site atual "Colin B Thoms": usei a grafia do briefing.
- [ ] **CNPJ.** Usei 26.427.026/0001-04 (matriz, do briefing). O site atual mostra 0004-57 (filial).
- [ ] **Horário de atendimento e coordenadas** não vieram no briefing, então ficaram fora do schema. Se informados, adicionar `openingHours` e `geo` em `locs_ld()`.
- [ ] **Google Business Profile** das duas unidades, se existirem, para incluir em `sameAs`.

## Fonte do conteúdo

- Briefing (Google Forms) e conversa com a Stella: história, fundadores, linhas, origens, endereços, telefones, paleta, sitemap, categorias com nomes próprios (ArtechLâminas, ArtechQuartzo, ArtechNano, Natural), marcador de Sold out.
- Site atual (artechstonebrasil.com.br): nomes das pedras, descrições técnicas das linhas, FAQ, ISO 9000, garantia ArtechNano, depoimentos (trechos curtos, nas outras línguas aparecem traduzidos e marcados como "Traduzido do português").
- Fotos: 22 fotos da Galeria em São Paulo (FD Fotografia), otimizadas de 20 a 36 MB para WebP de 60 a 400 KB. As fotos ilustram as linhas, mas não identificam o produto exato de cada chapa.
- O ArtechPrime existe no site atual, mas ficou fora porque não está nas categorias definidas pela Stella. A URL antiga redireciona para /pedras/.

## Logo

Logo oficial da pasta "00. lOGO" (BasicLogo - Stella Wong.svg), recortada sem a área vazia e gerada em duas versões: `logo.svg` (grafite, header ao rolar) e `logo-light.svg` (branca, header sobre o hero e rodapé). O símbolo sozinho virou `mark.svg`, `mark-light.svg`, favicon e ícones do app.

## Direção visual e animações

Seguindo as referências da Stella (Guilherme Torres, PNEU, Gray Puksand, Plus Studio, Architectus): títulos grandes em caixa alta, navegação espaçada, muita foto em sangria, blocos grafite e imagens deslocadas alternando lados.

- Abertura com o símbolo da marca girando e o logo se revelando (uma vez por sessão)
- Hero com título dividido em duas linhas que entram letra a letra; ao rolar, a foto encolhe para uma moldura e as linhas se afastam
- Scroll suave (Lenis) em todo o site
- Texto de apresentação que "acende" palavra por palavra conforme a rolagem, com contadores animados
- Linhas de produto no estilo PNEU: foto com revelação e parallax, nome gigante e seta
- Faixa com os mercados da fundadora que acelera com a velocidade da rolagem
- Galeria horizontal fixa na tela (telas acima de 1100 px) com parallax dentro de cada foto e barra de progresso
- "Para quem trabalhamos" troca a foto conforme o item
- Depoimentos em carrossel automático com barra de tempo
- Cursor personalizado (Ver, Ampliar), botões magnéticos e preenchimento ao passar o mouse
- Transição em cortina entre as páginas
- Tudo respeita "reduzir movimento" do sistema; sem JavaScript, o conteúdo aparece normalmente

## Formulários

Sem Apps Script: o formulário monta a mensagem com todos os campos e abre o WhatsApp (+55 28 3521-2416), depois leva para a página de obrigado. O botão nasce desabilitado e só libera com os campos obrigatórios válidos. Se o navegador bloquear a nova aba, a página de obrigado abre o WhatsApp na mesma aba.

## Eventos de rastreamento (dataLayer)

| Evento | Quando |
|---|---|
| `whatsapp_click` | qualquer botão de WhatsApp (`place`: menu, hero, float, footer, final, import, contact, faq, warranty, line-hero) |
| `stone_inquiry` | "Consultar esta pedra" (`place` = id da pedra) |
| `generate_lead` | envio de formulário (`form`: contact ou catalogue, `lang`) |
| `catalog_filter` | filtro de linha no catálogo |
| `gallery_open` | abrir foto da galeria |
| `language_switch` | troca de idioma |
| `phone_click`, `email_click` | cliques em tel: e mailto: |

## SEO, AEO e GEO

- [x] Title e meta description únicos por página e por idioma
- [x] Canonical, hreflang (pt-BR, en, es, zh-Hans, ja) e x-default em todas as páginas
- [x] Open Graph completo com og:locale e alternates, Twitter Card
- [x] JSON-LD em @graph: Organization (fundadores, CNPJ, marcas, redes), WebSite com SearchAction, WebPage/AboutPage/ContactPage/CollectionPage, BreadcrumbList, 2 HomeAndConstructionBusiness (ES e SP), ItemList de Product nas páginas de pedras, FAQPage (FAQ e páginas de linha)
- [x] Sitemap multilíngue com xhtml:link e image:image
- [x] robots.txt liberando GPTBot, ClaudeBot, PerplexityBot, Google-Extended e outros
- [x] llms.txt e llms-full.txt (fatos, linhas, URLs, FAQ em inglês e português)
- [x] Respostas diretas no começo de cada FAQ e bloco "Em resumo" na home, que é o formato que buscadores de IA citam
- [x] 301 das URLs do site antigo (WordPress) para as novas, para não perder posicionamento
- [x] Imagens WebP responsivas com srcset, width/height (CLS), lazy loading e preload do hero
- [x] Alt text descritivo em 5 idiomas e nomes de arquivo descritivos
- [x] HTML semântico, um H1 por página, breadcrumbs visíveis
- [x] Headers de segurança e cache de 1 ano para assets
- [x] 404 personalizada e página de obrigado com noindex
- [x] Fontes com preconnect e display=swap, Noto Sans SC/JP só nas páginas em chinês e japonês

Depois de publicar: enviar o sitemap no Google Search Console e no Bing Webmaster Tools, e testar uma página no Rich Results Test.
