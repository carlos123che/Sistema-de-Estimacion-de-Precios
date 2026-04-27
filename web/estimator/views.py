from django.shortcuts import render

def index(request):
    # Datos simulados para las propiedades de referencia
    propiedades_referencia = [
        {
            'titulo': 'Apartamento Z.14',
            'ubicacion': 'Edificio Las Américas',
            'area': '140 m²',
            'habs': '3 Hab.',
            'banos': '2.5 Baños',
            'parq': '2 Parq.',
            'precio': 'Q 1,320,000',
            'tipo': 'VENTA',
            'imagen': 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80'
        },
        {
            'titulo': 'Penthouse Boutique',
            'ubicacion': 'Zona 15, Vía 7',
            'area': '155 m²',
            'habs': '3 Hab.',
            'banos': '3 Baños',
            'parq': '2 Parq.',
            'precio': 'Q 1,450,000',
            'tipo': 'NUEVO',
            'imagen': 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80'
        }
    ]
    
    # Lista de zonas (puedes poblarla desde la base de datos más adelante)
    zonas = [
        "Zona 10, Ciudad de Guatemala",
        "Zona 14, Ciudad de Guatemala",
        "Zona 15, Ciudad de Guatemala",
        "Zona 16, Ciudad de Guatemala",
        "Carretera a El Salvador"
    ]

    context = {
        'propiedades': propiedades_referencia,
        'zonas': zonas,
        'precio_estimado': 'Q 1,250,000',
        'tendencia': '+2.4%'
    }
    
    return render(request, 'estimator/index.html', context)
