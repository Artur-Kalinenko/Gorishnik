{% extends "base.html" %}
{% load static %}

{% block title %}
    {{ assortment.assortment_name }}
{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <!-- Картинка -->
        <div class="col-md-6 text-center">
            {% if assortment.poster %}
                <img id="mainImage"
                     src="{{ assortment.poster.url }}"
                     class="main-image"
                     alt="{{ assortment.assortment_name }}">
            {% else %}
                <img id="mainImage"
                     src="{% static 'images/default.jpg' %}"
                     class="main-image"
                     alt="No image available">
            {% endif %}

            {% if images %}
                <div id="thumbnailGallery" class="d-flex flex-wrap justify-content-center mt-2">
                    {% if assortment.poster %}
                        <img src="{{ assortment.poster.url }}"
                             class="img-thumbnail m-1 thumbnail-img active-thumbnail"
                             style="height: 80px; width: auto; cursor: pointer;"
                             onclick="changeMainImage(this)">
                    {% else %}
                        <img src="{% static 'images/default.jpg' %}"
                             class="img-thumbnail m-1 thumbnail-img active-thumbnail"
                             style="height: 80px; width: auto; cursor: pointer;"
                             onclick="changeMainImage(this)">
                    {% endif %}

                    {% for img in images %}
                        <img src="{{ img.image.url }}"
                             class="img-thumbnail m-1 thumbnail-img"
                             style="height: 80px; width: auto; cursor: pointer;"
                             onclick="changeMainImage(this)">
                    {% endfor %}
                </div>
            {% endif %}
        </div>

        <!-- Инфо о товаре -->
        <div class="col-md-6">
            <h1 class="montserrat-category-title">{{ assortment.assortment_name }}</h1>
            <p><strong>Категорії:</strong>
                {% for cat in assortment.assortment_categories.all %}
                    <a href="{% url 'assortment_list' %}?category={{ cat.category }}" class="text-decoration-none">
                        {{ cat.category }}
                    </a>{% if not forloop.last %}, {% endif %}
                {% endfor %}
            </p>
            <p><strong>Виробник:</strong> {{ assortment.producer.producer_name }}</p>
            <p><strong>Наявність:</strong> {{ assortment.is_available|yesno:"У наявності,Нема у наявності" }}</p>
            <p><strong>Опис продукту:</strong></p>
            <p>{{ assortment.assortment_description }}</p>

            <!-- Ціна -->
            {% if variants.exists %}
                {% with sorted_variants=variants|dictsort:"price" %}
                    {% with min_variant=sorted_variants.0 %}
                        {% with last_variant=sorted_variants|slice:"-1"|first %}
                            {% with min_price=min_variant.price max_price=last_variant.price %}
                                {% if assortment.is_discounted and min_variant.old_price %}
                                    <p class="mb-1 text-muted text-decoration-line-through">
                                        {{ min_variant.old_price }} ₴{% if last_variant.old_price != min_variant.old_price %} – {{ last_variant.old_price }} ₴{% endif %}
                                    </p>
                                    <p class="fw-bold text-danger mb-2">
                                        {{ min_price }} ₴{% if max_price != min_price %} – {{ max_price }} ₴{% endif %}
                                    </p>
                                {% else %}
                                    <p class="fw-bold mb-2">
                                        {{ min_price }} ₴{% if max_price != min_price %} – {{ max_price }} ₴{% endif %}
                                    </p>
                                {% endif %}
                            {% endwith %}
                        {% endwith %}
                    {% endwith %}
                {% endwith %}
            {% else %}
                {% if assortment.is_discounted and assortment.old_price %}
                    <p class="mb-1 text-muted text-decoration-line-through">{{ assortment.old_price }} ₴</p>
                    <p class="fw-bold text-danger">{{ assortment.price }} ₴</p>
                {% else %}
                    <p class="fw-bold">{{ assortment.price }} ₴</p>
                {% endif %}
            {% endif %}

            <!-- Варианты -->
            {% if variants.exists %}
                <div class="mb-3">
                    {% for variant in variants %}
                        <button class="btn btn-outline-secondary grams-button btn-sm"
                                data-price="{{ variant.price }}"
                                data-old-price="{{ variant.old_price }}">
                            {{ variant.grams }}г
                        </button>
                    {% endfor %}
                </div>
                <div id="variant-price-output" class="mt-2"></div>
            {% else %}
                <p class="card-text">{{ assortment.grams }}г</p>
            {% endif %}
        </div>
    </div>
</div>

<link rel="stylesheet" href="{% static 'assortment/assortment_detail.css' %}">
<script src="{% static 'assortment/assortment_detail.js' %}"></script>
{% endblock %}
