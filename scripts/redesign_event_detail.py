#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para rediseñar completamente la plantilla public_detail.html
"""

NEW_TEMPLATE = """{% load static %}
{% load i18n %}
{% load translation_tags %}
{% get_current_language as CURRENT_LANGUAGE %}
<!DOCTYPE html>
<html lang="{% if CURRENT_LANGUAGE %}{{ CURRENT_LANGUAGE|slice:":2" }}{% else %}en{% endif %}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ event.title }} - {% trans "NCS International" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">

    <style>
        :root {
            --mlb-blue: #0d2c54;
            --mlb-red: #d50032;
            --mlb-light-blue: #132448;
            --mlb-gold: #ffd700;
            --mlb-dark: #1a1a1a;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
        }

        /* Navbar styles removed - using includes */

        /* Hero Minimalista */
        .hero {
            background: linear-gradient(135deg, var(--mlb-blue) 0%, var(--mlb-light-blue) 100%);
            color: white;
            padding: 60px 20px;
            position: relative;
            overflow: hidden;
        }

        .hero::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--mlb-red) 0%, var(--mlb-gold) 50%, var(--mlb-red) 100%);
        }

        .hero-content {
            max-width: 800px;
            margin: 0 auto;
            text-align: center;
        }

        .breadcrumb-simple {
            font-size: 0.875rem;
            color: #6b7280;
            margin-bottom: 20px;
        }

        .breadcrumb-simple a {
            color: var(--primary);
            text-decoration: none;
        }

        .event-title-main {
            font-size: 2.5rem;
            font-weight: 700;
            color: white;
            margin-bottom: 15px;
            line-height: 1.2;
        }

        .event-subtitle-main {
            font-size: 1.125rem;
            color: rgba(255,255,255,0.9);
            margin-bottom: 30px;
        }

        .meta-badges {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }

        .badge-item {
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            padding: 10px 20px;
            border-radius: 50px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.875rem;
            font-weight: 500;
            border: 1px solid rgba(255,255,255,0.2);
        }

        .badge-item i {
            color: var(--mlb-gold);
        }

        /* Container Principal */
        .main-container {
            max-width: 1200px;
            margin: 0 auto 60px;
            padding: 0 20px;
        }

        /* Cards Flotantes */
        .card-section {
            background: white;
            border-radius: 16px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .card-section:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.12);
        }

        .card-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--mlb-blue);
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid var(--mlb-blue);
            display: inline-block;
        }

        /* Info Grid Moderno */
        .info-grid-modern {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }

        .info-box {
            text-align: center;
            padding: 20px;
            background: var(--light);
            border-radius: 12px;
            transition: all 0.3s;
        }

        .info-box:hover {
            background: var(--mlb-blue);
            color: white;
            transform: scale(1.05);
        }

        .info-box i {
            font-size: 2rem;
            color: var(--mlb-blue);
            margin-bottom: 10px;
            display: block;
        }

        .info-box:hover i {
            color: white;
        }

        .info-box-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin-bottom: 5px;
            opacity: 0.7;
        }

        .info-box-value {
            font-size: 1.125rem;
            font-weight: 700;
        }

        /* Tabla de Precios Moderna */
        .price-table-modern {
            width: 100%;
        }

        .price-row-modern {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid #e5e7eb;
            transition: background 0.2s;
        }

        .price-row-modern:hover {
            background: var(--light);
        }

        .price-row-modern:last-child {
            border-bottom: none;
        }

        .price-label-modern {
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 600;
            color: #374151;
        }

        .price-label-modern i {
            width: 30px;
            height: 30px;
            background: var(--mlb-blue);
            color: white;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.875rem;
        }

        .price-value-modern {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--mlb-red);
        }

        /* Modal Moderno */
        .modal-modern .modal-content {
            border-radius: 16px;
            border: none;
            overflow: hidden;
        }

        .modal-modern .modal-header {
            background: linear-gradient(135deg, var(--mlb-blue) 0%, var(--mlb-light-blue) 100%);
            color: white;
            padding: 30px;
            border: none;
            position: relative;
        }

        .modal-modern .modal-header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--mlb-red) 0%, var(--mlb-gold) 50%, var(--mlb-red) 100%);
        }

        .modal-modern .modal-title {
            font-size: 1.75rem;
            font-weight: 700;
        }

        .modal-modern .modal-body {
            padding: 40px;
        }

        .type-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }

        .type-option {
            background: var(--light);
            border: 3px solid transparent;
            border-radius: 16px;
            padding: 30px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }

        .type-option:hover {
            border-color: var(--mlb-blue);
            background: white;
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(13,44,84,0.15);
        }

        .type-option.active {
            background: var(--mlb-blue);
            border-color: var(--mlb-blue);
            color: white;
        }

        .type-option i {
            font-size: 3rem;
            margin-bottom: 15px;
            display: block;
            color: var(--mlb-blue);
        }

        .type-option.active i {
            color: white;
        }

        .type-option span {
            font-weight: 600;
            font-size: 1rem;
        }

        /* FAB */
        .fab {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: var(--mlb-blue);
            color: white;
            border-radius: 50%;
            display: none;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            box-shadow: 0 4px 15px rgba(13,44,84,0.4);
            cursor: pointer;
            transition: all 0.3s;
            border: none;
            z-index: 999;
        }

        .fab:hover {
            transform: scale(1.1);
            background: var(--mlb-red);
        }

        /* CTA Final */
        .cta-final {
            background: linear-gradient(135deg, var(--mlb-blue) 0%, var(--mlb-light-blue) 100%);
            color: white;
            padding: 60px 40px;
            border-radius: 16px;
            text-align: center;
            margin-top: 40px;
            position: relative;
            overflow: hidden;
        }

        .cta-final::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--mlb-red) 0%, var(--mlb-gold) 50%, var(--mlb-red) 100%);
        }

        .cta-final h3 {
            font-size: 2rem;
            margin-bottom: 15px;
        }

        .cta-final p {
            font-size: 1.125rem;
            opacity: 0.9;
            margin-bottom: 30px;
        }

        .btn-group-cta {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }

        .btn-cta {
            padding: 15px 35px;
            border-radius: 50px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }

        .btn-cta-primary {
            background: var(--mlb-red);
            color: white;
        }

        .btn-cta-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(255,255,255,0.3);
        }

        .btn-cta-outline {
            background: transparent;
            color: white;
            border: 2px solid white;
        }

        .btn-cta-outline:hover {
            background: rgba(255,255,255,0.2);
            border-color: white;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .hero { padding: 40px 20px; margin: 20px; }
            .event-title-main { font-size: 2rem; }
            .card-section { padding: 25px; }
            .type-grid { grid-template-columns: 1fr; }
            .info-grid-modern { grid-template-columns: 1fr; }
            .nav-links { display: none; }
            .btn-group-cta { flex-direction: column; }
            .btn-cta { width: 100%; justify-content: center; }
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    {% include 'includes/navbar_mlb.html' %}

    <!-- Modal -->
    <div class="modal fade modal-modern" id="typeModal" data-bs-backdrop="static" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 class="modal-title">{% trans "Select Your Registration Type" %}</h2>
                </div>
                <div class="modal-body">
                    <div class="type-grid">
                        <div class="type-option" data-type="player">
                            <i class="fas fa-user"></i>
                            <span>{% trans "Individual Player" %}</span>
                        </div>
                        <div class="type-option" data-type="team_manager">
                            <i class="fas fa-users"></i>
                            <span>{% trans "Team Manager" %}</span>
                        </div>
                        <div class="type-option" data-type="spectator">
                            <i class="fas fa-eye"></i>
                            <span>{% trans "Spectator" %}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- FAB -->
    <button class="fab" id="fabBtn"><i class="fas fa-sync-alt"></i></button>

    <!-- Hero -->
    <div class="hero">
        <div class="hero-content">
            <div class="breadcrumb-simple">
                <a href="/">{% trans "Home" %}</a> / <a href="{% url 'events:public_list' %}">{% trans "Events" %}</a> / {{ event.title|truncatechars:30 }}
            </div>
            <h1 class="event-title-main">{{ event.title }}</h1>
            {% if event.short_name %}
                <p class="event-subtitle-main">{{ event.short_name }}</p>
            {% endif %}
            <div class="meta-badges">
                {% if event.start_date %}
                <div class="badge-item">
                    <i class="fas fa-calendar"></i>
                    {{ event.start_date|date:"M d, Y" }}
                </div>
                {% endif %}
                {% if event.city %}
                <div class="badge-item">
                    <i class="fas fa-map-marker-alt"></i>
                    {{ event.city.name }}
                </div>
                {% endif %}
                {% if event.entry_deadline %}
                <div class="badge-item">
                    <i class="fas fa-clock"></i>
                    {% trans "Deadline" %}: {{ event.entry_deadline|date:"M d" }}
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-container" id="mainContent" style="display:none;">
        <!-- Details -->
        <div class="card-section">
            <h2 class="card-title">{% trans "Event Details" %}</h2>
            <div class="info-grid-modern">
                {% if event.start_date %}
                <div class="info-box">
                    <i class="fas fa-calendar-check"></i>
                    <div class="info-box-label">{% trans "Start" %}</div>
                    <div class="info-box-value">{{ event.start_date|date:"M d, Y" }}</div>
                </div>
                {% endif %}
                {% if event.end_date %}
                <div class="info-box">
                    <i class="fas fa-calendar-times"></i>
                    <div class="info-box-label">{% trans "End" %}</div>
                    <div class="info-box-value">{{ event.end_date|date:"M d, Y" }}</div>
                </div>
                {% endif %}
                {% if event.city %}
                <div class="info-box">
                    <i class="fas fa-map-pin"></i>
                    <div class="info-box-label">{% trans "Location" %}</div>
                    <div class="info-box-value">{{ event.city.name }}</div>
                </div>
                {% endif %}
                {% if event.entry_deadline %}
                <div class="info-box">
                    <i class="fas fa-hourglass-half"></i>
                    <div class="info-box-label">{% trans "Deadline" %}</div>
                    <div class="info-box-value">{{ event.entry_deadline|date:"M d, Y" }}</div>
                </div>
                {% endif %}
            </div>
        </div>

        <!-- Description -->
        <div class="card-section">
            <h2 class="card-title">{% trans "About" %}</h2>
            <div class="content-type" id="desc-player" style="display:none;">{{ event.description|safe }}</div>
            <div class="content-type" id="desc-team_manager" style="display:none;">{{ event.description_team_manager|default:event.description|safe }}</div>
            <div class="content-type" id="desc-spectator" style="display:none;">{{ event.description_spectator|default:event.description|safe }}</div>
        </div>

        <!-- Pricing -->
        <div class="card-section">
            <h2 class="card-title">{% trans "Pricing" %}</h2>
            <div class="content-type" id="price-player" style="display:none;">
                <div class="price-table-modern">
                    {% if event.default_entry_fee %}
                    <div class="price-row-modern">
                        <div class="price-label-modern">
                            <i class="fas fa-ticket-alt"></i>
                            {% trans "Entry Fee" %}
                        </div>
                        <div class="price-value-modern">${{ event.default_entry_fee|floatformat:2 }}</div>
                    </div>
                    {% endif %}
                    {% if event.gate_fee_amount %}
                    <div class="price-row-modern">
                        <div class="price-label-modern">
                            <i class="fas fa-door-open"></i>
                            {% trans "Gate Fee" %}
                        </div>
                        <div class="price-value-modern">${{ event.gate_fee_amount|floatformat:2 }}</div>
                    </div>
                    {% endif %}
                </div>
            </div>
            <div class="content-type" id="price-team_manager" style="display:none;">
                <div class="price-table-modern">
                    {% if event.default_entry_fee_team_manager or event.default_entry_fee %}
                    <div class="price-row-modern">
                        <div class="price-label-modern">
                            <i class="fas fa-ticket-alt"></i>
                            {% trans "Entry Fee" %}
                        </div>
                        <div class="price-value-modern">${{ event.default_entry_fee_team_manager|default:event.default_entry_fee|floatformat:2 }}</div>
                    </div>
                    {% endif %}
                    {% if event.gate_fee_amount_team_manager or event.gate_fee_amount %}
                    <div class="price-row-modern">
                        <div class="price-label-modern">
                            <i class="fas fa-door-open"></i>
                            {% trans "Gate Fee" %}
                        </div>
                        <div class="price-value-modern">${{ event.gate_fee_amount_team_manager|default:event.gate_fee_amount|floatformat:2 }}</div>
                    </div>
                    {% endif %}
                </div>
            </div>
            <div class="content-type" id="price-spectator" style="display:none;">
                <div class="price-table-modern">
                    {% if event.default_entry_fee_spectator or event.default_entry_fee %}
                    <div class="price-row-modern">
                        <div class="price-label-modern">
                            <i class="fas fa-ticket-alt"></i>
                            {% trans "Entry Fee" %}
                        </div>
                        <div class="price-value-modern">${{ event.default_entry_fee_spectator|default:event.default_entry_fee|floatformat:2 }}</div>
                    </div>
                    {% endif %}
                    {% if event.gate_fee_amount_spectator or event.gate_fee_amount %}
                    <div class="price-row-modern">
                        <div class="price-label-modern">
                            <i class="fas fa-door-open"></i>
                            {% trans "Gate Fee" %}
                        </div>
                        <div class="price-value-modern">${{ event.gate_fee_amount_spectator|default:event.gate_fee_amount|floatformat:2 }}</div>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- CTA -->
        <div class="cta-final">
            <h3>{% trans "Ready to Register?" %}</h3>
            <p>{% trans "Join us for an amazing event experience" %}</p>
            <div class="btn-group-cta">
                {% if not user.is_authenticated %}
                <a href="/accounts/register/" class="btn-cta btn-cta-primary">
                    <i class="fas fa-user-plus"></i> {% trans "Register Now" %}
                </a>
                {% endif %}
                <a href="{% url 'events:public_list' %}" class="btn-cta btn-cta-outline">
                    <i class="fas fa-calendar"></i> {% trans "View All Events" %}
                </a>
            </div>
        </div>
    </div>

    <!-- Footer -->
    {% include 'includes/footer_mlb.html' %}

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const modal = new bootstrap.Modal(document.getElementById('typeModal'));
            const options = document.querySelectorAll('.type-option');
            const content = document.getElementById('mainContent');
            const fab = document.getElementById('fabBtn');
            const key = 'userType_{{ event.id }}';
            let selected = localStorage.getItem(key);

            if (selected) {
                showContent(selected);
            } else {
                modal.show();
            }

            options.forEach(opt => {
                opt.addEventListener('click', function() {
                    options.forEach(o => o.classList.remove('active'));
                    this.classList.add('active');
                    selected = this.dataset.type;
                    localStorage.setItem(key, selected);
                    setTimeout(() => {
                        modal.hide();
                        showContent(selected);
                    }, 300);
                });
            });

            fab.addEventListener('click', () => {
                options.forEach(o => {
                    o.classList.remove('active');
                    if (o.dataset.type === selected) o.classList.add('active');
                });
                modal.show();
            });

            function showContent(type) {
                document.querySelectorAll('.content-type').forEach(el => el.style.display = 'none');
                const desc = document.getElementById(`desc-${type}`);
                const price = document.getElementById(`price-${type}`);
                if (desc) desc.style.display = 'block';
                if (price) price.style.display = 'block';
                content.style.display = 'block';
                fab.style.display = 'flex';
            }
        });
    </script>
</body>
</html>
"""

def main():
    import os
    file_path = os.path.join('templates', 'events', 'public_detail.html')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(NEW_TEMPLATE)

    print(f"Plantilla redise;ada exitosamente: {file_path}")
    print("Nuevo dise;o aplicado con:")
    print("   - Hero minimalista con badges")
    print("   - Cards flotantes con hover effects")
    print("   - Colores modernos (azul/purpura)")
    print("   - Grid responsive")
    print("   - Modal con nuevo dise;o")

if __name__ == '__main__':
    main()
