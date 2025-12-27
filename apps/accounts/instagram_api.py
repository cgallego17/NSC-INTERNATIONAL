"""
Instagram API Integration
Para usar Instagram Basic Display API o Graph API
"""

import json
import re
import requests
from django.conf import settings


def get_instagram_posts(username=None, limit=6):
    """
    Obtiene los últimos posts de Instagram desde RSS feed

    Args:
        username: Username de Instagram (no usado, mantenido para compatibilidad)
        limit: Número de posts a obtener (por defecto 6)

    Returns:
        Lista de posts con imagen, URL, y metadata
    """
    # Usar solo RSS feed
    rss_feed_url = getattr(settings, "INSTAGRAM_RSS_FEED_URL", None)
    if rss_feed_url:
        try:
            posts = get_instagram_posts_from_rss(rss_feed_url, limit)
            if posts:
                return posts
        except Exception as e:
            print(f"Error obteniendo posts desde RSS feed: {e}")
            import traceback

            traceback.print_exc()

    # Si no hay RSS feed configurado o falla, retornar lista vacía
    print(
        f"Advertencia: No se pudo obtener posts de Instagram. RSS feed URL: {rss_feed_url}"
    )
    return []


def get_instagram_user_id(username, access_token):
    """
    Obtiene el user_id de Instagram usando el username
    """
    try:
        # Buscar el user_id usando el username
        # Nota: Esto requiere que tengas el username configurado en tu app de Facebook
        url = f"https://graph.instagram.com/me"
        params = {"fields": "id,username", "access_token": access_token}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        return data.get("id")

    except Exception as e:
        print(f"Error obteniendo user_id de Instagram: {e}")
        return None


def get_instagram_profile(username=None, access_token=None):
    """
    Obtiene la información del perfil de Instagram

    Returns:
        Dict con información del perfil (display_name, profile_picture, followers_count, etc.)
    """
    if not access_token:
        access_token = getattr(settings, "INSTAGRAM_ACCESS_TOKEN", None)

    if not access_token:
        return {}

    try:
        # Obtener información del perfil usando Instagram Graph API
        user_id = get_instagram_user_id(username, access_token)

        if not user_id:
            return {}

        # Obtener información del perfil
        url = f"https://graph.instagram.com/{user_id}"
        params = {"fields": "id,username,account_type", "access_token": access_token}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Para obtener más información (seguidores, etc.) necesitarías usar Facebook Graph API
        # con permisos adicionales

        profile = {
            "username": data.get("username", username),
            "display_name": data.get("username", username).replace("_", " ").title(),
            "account_type": data.get("account_type"),
        }

        return profile

    except Exception as e:
        print(f"Error obteniendo perfil de Instagram: {e}")
        return {}


def get_instagram_posts_from_rss(rss_url, limit=6):
    """
    Obtiene posts de Instagram desde un RSS feed

    Args:
        rss_url: URL del RSS feed (ej: desde RSS.app)
        limit: Número de posts a obtener

    Returns:
        Lista de posts con imagen, URL, y metadata
    """
    try:
        import xml.etree.ElementTree as ET

        response = requests.get(
            rss_url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        response.raise_for_status()

        root = ET.fromstring(response.text)
        posts = []

        # Namespace para media (RSS.app usa media:content)
        namespaces = {
            "media": "http://search.yahoo.com/mrss/",
            "dc": "http://purl.org/dc/elements/1.1/",
        }

        # Obtener todos los items disponibles del RSS feed
        all_items = root.findall(".//item")

        print(f"[DEBUG] RSS feed contiene {len(all_items)} items disponibles")

        # Procesar todos los items disponibles hasta alcanzar el límite
        processed_count = 0
        for item in all_items:
            if processed_count >= limit:
                break
            title = item.find("title")
            link = item.find("link")
            description = item.find("description")
            pub_date = item.find("pubDate")

            # Intentar obtener imagen desde media:content (más confiable en RSS.app)
            image_url = None
            media_content = item.find("media:content", namespaces)
            if media_content is not None:
                image_url = media_content.get("url")
                # Limpiar entidades HTML
                if image_url:
                    image_url = image_url.replace("&amp;", "&")

            # Si no hay media:content, buscar en description
            if not image_url and description is not None:
                desc_text = description.text or ""
                # Buscar URL de imagen en el HTML de description
                img_match = re.search(r'<img[^>]*src=["\']([^"\']+)["\']', desc_text)
                if img_match:
                    image_url = img_match.group(1)
                    # Limpiar la URL (puede tener entidades HTML)
                    image_url = image_url.replace("&amp;", "&")

            # Obtener título y link
            title_text = title.text if title is not None and title.text else ""
            # Limpiar CDATA si está presente
            if title_text and "<![CDATA[" in title_text:
                title_text = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", title_text)

            link_url = link.text if link is not None and link.text else ""

            if image_url:
                posts.append(
                    {
                        "id": f"rss_{len(posts)}",
                        "image_url": image_url,
                        "permalink": link_url
                        or f"https://www.instagram.com/{getattr(settings, 'INSTAGRAM_USERNAME', 'ncs_international')}/",
                        "caption": title_text,
                        "media_type": "image",
                    }
                )
                processed_count += 1

        # Retornar exactamente el número solicitado (hasta el límite disponible)
        final_posts = posts[:limit]
        print(
            f"[OK] Encontrados {len(final_posts)} posts válidos desde RSS feed (solicitados: {limit}, items disponibles: {len(all_items)}): {rss_url}"
        )
        return final_posts

    except Exception as e:
        print(f"Error parseando RSS feed: {e}")
        import traceback

        traceback.print_exc()
        return []


def get_instagram_posts_from_profile(username, limit=12):
    """
    Obtiene posts de Instagram desde el perfil público

    Métodos intentados (en orden de prioridad):
    1. RSS Feed de Instagram (si está disponible)
    2. Scraping del HTML (puede no funcionar debido a restricciones de Instagram)
    3. Servicios de terceros (requieren configuración adicional)

    Nota: Desde diciembre 2024, Instagram Basic Display API fue deprecada.
    La única forma oficial es usar Instagram Graph API con cuenta Business/Creator.

    Args:
        username: Username de Instagram (sin @)
        limit: Número de posts a obtener

    Returns:
        Lista de posts con imagen, URL, y metadata
    """
    # Método 1: Intentar obtener desde RSS feed usando diferentes servicios
    rss_services = [
        f"https://rss.app/rss-feed/instagram/{username}",
        f"https://www.instagram.com/{username}/feed/?__a=1&__d=dis",  # Endpoint antiguo (puede no funcionar)
    ]

    for rss_url in rss_services:
        try:
            response = requests.get(
                rss_url,
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                if "xml" in content_type or "rss" in content_type:
                    # Parsear RSS feed
                    import xml.etree.ElementTree as ET

                    try:
                        root = ET.fromstring(response.text)
                        posts = []
                        for item in root.findall(".//item")[:limit]:
                            title = item.find("title")
                            link = item.find("link")
                            description = item.find("description")

                            if description is not None:
                                desc_text = description.text or ""
                                img_match = re.search(
                                    r'<img[^>]*src="([^"]+)"', desc_text
                                )
                                if img_match:
                                    posts.append(
                                        {
                                            "id": f"rss_{len(posts)}",
                                            "image_url": img_match.group(1),
                                            "permalink": (
                                                link.text
                                                if link is not None
                                                else f"https://www.instagram.com/{username}/"
                                            ),
                                            "caption": (
                                                title.text if title is not None else ""
                                            ),
                                            "media_type": "image",
                                        }
                                    )
                        if posts:
                            print(f"Encontrados {len(posts)} posts desde RSS feed")
                            return posts[:limit]
                    except ET.ParseError:
                        continue
        except Exception as e:
            print(f"Error obteniendo RSS feed desde {rss_url}: {e}")
            continue

    # Método 2: Scraping del HTML (método anterior - puede no funcionar)
    try:
        url = f"https://www.instagram.com/{username}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        html = response.text
        print(f"HTML obtenido: {len(html)} caracteres")
        print(f"URL: {url}")
        print(f"Status code: {response.status_code}")

        # Buscar el JSON embebido en la página
        # Instagram ahora usa diferentes estructuras, intentamos varios patrones
        data = None

        # Patrón 1: window._sharedData (estructura antigua)
        pattern = r"window\._sharedData\s*=\s*({.+?});"
        match = re.search(pattern, html)
        if match:
            try:
                data = json.loads(match.group(1))
            except:
                pass

        # Patrón 2: JSON en script tags con type="application/json"
        if not data:
            pattern = r'<script type="application/json"[^>]*>(.+?)</script>'
            matches = re.findall(pattern, html, re.DOTALL)
            for match_text in matches:
                try:
                    temp_data = json.loads(match_text)
                    # Buscar datos del usuario en diferentes estructuras
                    if (
                        "entry_data" in temp_data
                        or "graphql" in match_text
                        or "ProfilePage" in match_text
                    ):
                        data = temp_data
                        break
                except:
                    continue

        # Patrón 3: Buscar en window.__additionalDataLoaded
        if not data:
            pattern = r"window\.__additionalDataLoaded[^;]*\([^,]*,\s*({.+?})\);"
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                except:
                    pass

        # Patrón 4: Buscar cualquier JSON grande que contenga "ProfilePage" o "graphql"
        if not data:
            pattern = r'<script[^>]*>(.*?"ProfilePage".*?)</script>'
            match = re.search(pattern, html, re.DOTALL)
            if match:
                # Intentar extraer JSON del script
                script_content = match.group(1)
                json_pattern = r'({[^{}]*"ProfilePage"[^{}]*})'
                json_match = re.search(json_pattern, script_content)
                if json_match:
                    try:
                        data = json.loads(json_match.group(1))
                    except:
                        pass

        if not data:
            return []

        posts = []

        # Navegar por la estructura de datos de Instagram
        # La estructura puede variar, intentamos diferentes rutas
        edges = []

        try:
            # Estructura común de Instagram (antigua)
            if "entry_data" in data:
                user_data = (
                    data.get("entry_data", {})
                    .get("ProfilePage", [{}])[0]
                    .get("graphql", {})
                    .get("user", {})
                )
                edges = user_data.get("edge_owner_to_timeline_media", {}).get(
                    "edges", []
                )
            # Estructura alternativa
            elif "graphql" in str(data):
                # Buscar en diferentes niveles
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, dict) and "user" in value:
                            user_data = value.get("user", {})
                            edges = user_data.get(
                                "edge_owner_to_timeline_media", {}
                            ).get("edges", [])
                            if edges:
                                break

            if edges:
                for edge in edges[:limit]:
                    node = edge.get("node", {})
                    if node.get("__typename") == "GraphImage":
                        image_url = node.get("display_url") or node.get("thumbnail_src")
                    elif node.get("__typename") == "GraphVideo":
                        image_url = node.get("thumbnail_src")
                    elif node.get("__typename") == "GraphSidecar":
                        # Para carousels, usar la primera imagen
                        first_edge = node.get("edge_sidecar_to_children", {}).get(
                            "edges", [{}]
                        )[0]
                        first_node = first_edge.get("node", {})
                        image_url = first_node.get("display_url") or first_node.get(
                            "thumbnail_src"
                        )
                    else:
                        image_url = node.get("display_url") or node.get("thumbnail_src")

                    shortcode = node.get("shortcode")
                    permalink = (
                        f"https://www.instagram.com/p/{shortcode}/"
                        if shortcode
                        else None
                    )

                    caption_edges = node.get("edge_media_to_caption", {}).get(
                        "edges", []
                    )
                    caption = (
                        caption_edges[0].get("node", {}).get("text", "")
                        if caption_edges
                        else ""
                    )

                    if image_url:
                        posts.append(
                            {
                                "id": node.get("id"),
                                "image_url": image_url,
                                "permalink": permalink,
                                "caption": (
                                    caption[:100] + "..."
                                    if len(caption) > 100
                                    else caption
                                ),
                                "media_type": node.get("__typename", "IMAGE")
                                .replace("Graph", "")
                                .lower(),
                            }
                        )
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error parseando estructura de Instagram: {e}")
            import traceback

            traceback.print_exc()

        # Si no se encontraron posts con el método principal, intentar método alternativo
        if not posts or len(posts) == 0:
            print(
                f"No se encontraron posts con método principal, intentando método alternativo..."
            )
            try:
                # Buscar URLs de imágenes de Instagram en el HTML usando múltiples patrones
                img_patterns = [
                    r'"display_url":"([^"]+)"',
                    r'"thumbnail_src":"([^"]+)"',
                    r'"src":"([^"]*scontent[^"]*)"',
                    r'https://[^"]*scontent[^"]*\.(?:jpg|jpeg|png|webp)',
                    r'https://[^"]*cdninstagram[^"]*\.(?:jpg|jpeg|png|webp)',
                    r'<img[^>]*src="([^"]*scontent[^"]*)"[^>]*>',
                    r'<img[^>]*src="([^"]*cdninstagram[^"]*)"[^>]*>',
                    r'url\(["\']?([^"\']*scontent[^"\']*)["\']?\)',
                ]

                found_urls = set()
                print(f"Buscando imágenes con {len(img_patterns)} patrones...")
                for i, pattern in enumerate(img_patterns):
                    img_matches = re.findall(pattern, html, re.IGNORECASE)
                    print(f"Patrón {i+1}: {len(img_matches)} coincidencias")
                    for img_url in img_matches:
                        # Si es una tupla (del patrón con grupos), tomar solo la URL
                        if isinstance(img_url, tuple):
                            continue
                        # Limpiar la URL
                        img_url = (
                            img_url.replace("\\u0026", "&")
                            .replace("\\/", "/")
                            .replace("\\", "")
                            .replace("\\u003d", "=")
                        )
                        # Verificar que sea una URL válida de Instagram
                        if any(
                            domain in img_url
                            for domain in ["scontent", "cdninstagram", "fbcdn"]
                        ):
                            # Asegurar que tenga protocolo
                            if not img_url.startswith("http"):
                                if img_url.startswith("//"):
                                    img_url = "https:" + img_url
                                else:
                                    continue
                            if img_url not in found_urls:
                                found_urls.add(img_url)
                                posts.append(
                                    {
                                        "id": f"scraped_{len(posts)}",
                                        "image_url": img_url,
                                        "permalink": f"https://www.instagram.com/{username}/",
                                        "caption": "",
                                        "media_type": "image",
                                    }
                                )
                                print(
                                    f"Agregada imagen {len(posts)}: {img_url[:80]}..."
                                )
                                if len(posts) >= limit:
                                    break
                    if len(posts) >= limit:
                        break

                print(f"Encontradas {len(posts)} imágenes usando método alternativo")
            except Exception as e2:
                print(f"Error en método alternativo: {e2}")
                import traceback

                traceback.print_exc()

        print(f"Total de posts encontrados: {len(posts)}")
        return posts[:limit]

    except Exception as e:
        print(f"Error obteniendo posts desde perfil público: {e}")
        import traceback

        traceback.print_exc()
        return []













