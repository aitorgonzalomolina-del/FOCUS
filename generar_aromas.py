"""
Genera descripciones de aroma para todos los productos del catálogo.
Las agrega como campo 'aroma' en catalogo.js
"""
import json, re

# ─── Descripciones específicas por producto (nombre exacto sin prefijo de categoría) ───
ESPECIFICOS = {
    # AFNAN
    "AFNAN 9PM EDP":                        "Amaderado especiado con notas de cardamomo, ámbar y vainilla oscura.",
    "AFNAN 9PM ELIXIR PARFUM INTENSE":      "Versión intensa del 9PM: oud, cuero y ámbar en una base profunda y sensual.",

    # AL HARAMAIN
    "AL HARAMAIN AMBER OUD DUBAI NIGHT EDP":        "Oud nocturno con ámbar intenso, cuero oscuro y notas especiadas.",
    "AL HARAMAIN AMBER OUD GOLD 999.9 DUBAI EDITION EDP": "Ámbar dorado lujoso con oud puro de Dubái, vainilla y especias orientales.",
    "AL HARAMAIN AMBER OUD GOLD EDP":               "Cálido ámbar dorado con oud elegante, sándalo y acordes especiados.",

    # AL WATANIAH
    "AL WATANIAH ABYAT EDP":                "Floral oriental con notas de rosa blanca, almizcle y oud suave.",
    "AL WATANIAH AMEERATI EDP":             "Floral femenino con jazmín, oud dulce y fondo ambarado.",
    "AL WATANIAH ATTAR AL WESAL EDP":       "Oriental romántico con rosa, oud y un dulce fondo de almizcle.",
    "AL WATANIAH BAREEQ AL DHAHAB EDP":     "Brillante y dorado: ámbar, vainilla y notas florales orientales.",
    "AL WATANIAH KENZ AL MALIK EDP":        "Real y especiado, con oud, cuero y notas de incienso.",
    "AL WATANIAH OUD MSYTERY INTENSE EDP":  "Oud misterioso e intenso, ahumado con notas de cuero y resina.",
    "AL WATANIAH ROSE MYSTERY INTENSE EDP": "Rosa intensa con almizcle, oud y un velo de especias orientales.",
    "AL WATANIAH SABAH AL WARD EDP":        "Mañana de rosas: floral fresco con rosa, bergamota y almizcle suave.",
    "AL WATANIAH SABAH AL WARD SUGAR EDP":  "Rosa azucarada con notas de frutos rojos, vainilla y almizcle.",
    "AL WATANIAH SABAH AL WARD VALENTINE EDP": "Rosa romántica con corazón de jazmín y fondo de ámbar dulce.",
    "AL WATANIAH SHAGAF AL WARD EDP":       "Pasión floral: rosas intensas con oud y almizcle cálido.",
    "AL WATANIAH SPECIAL OUD EDP":          "Oud especial de Arabia, puro y profundo con resinas y especias.",
    "AL WATANIAH SULTAN AL LAIL EDP":       "Nocturno y poderoso: oud oscuro, incienso y cuero sobre ámbar.",
    "AL WATANIAH THAHAANI EDP":             "Oriental festivo con rosa, oud y notas especiadas cálidas.",
    "AL WATANIAH TIARA EDP":                "Elegante y coronado: floral blanco con almizcle y sándalo.",

    # ARMAF
    "ARMAF BEACH PARTY EDP":               "Fresco marino con cítricos, notas acuáticas y fondo amaderado.",
    "ARMAF CHECKMATE KING EDP":            "Fougère masculino con lavanda, madera y notas especiadas.",
    "ARMAF CHECKMATE QUEEN EDP":           "Floral frutal femenino con pera, jazmín y almizcle suave.",
    "ARMAF CLUB DE NUIT BLING EDP":        "Frutal floral chispeante con notas cítricas, rosa y ámbar.",
    "ARMAF CLUB DE NUIT IMPERIALE EDP":    "Imperial y especiado: notas cítricas, especias y base amaderada.",
    "ARMAF CLUB DE NUIT INTENSE MAN EDT":  "Clásico amaderado con notas de abedul, ámbar y almizcle ahumado.",
    "ARMAF CLUB DE NUIT LIONHEART MAN EDP": "Audaz y masculino: cardamomo, notas amaderadas y almizcle.",
    "ARMAF CLUB DE NUIT LIONHEART WOMAN EDP": "Floral frutal femenino con notas de pera, rosa y vainilla.",
    "ARMAF CLUB DE NUIT MILESTONE EDP":    "Amaderado especiado con notas de pachulí, ámbar y cuero.",
    "ARMAF CLUB DE NUIT PRECIEUX IV EXTRAIT DE PARFUM": "Extrait de lujo: oud, rosa turca y ámbar en máxima concentración.",
    "ARMAF CLUB DE NUIT PRECIEUX I EXTRAIT DE PARFUM":  "Extrait oriental: especias, ámbar y madera de sándalo puro.",
    "ARMAF CLUB DE NUIT SILLAGE EDP":      "Estela larga y sensual: notas florales, almizcle y madera oscura.",
    "ARMAF CLUB DE NUIT UNTOLD EDP":       "Historia secreta: rosa, pachulí y notas ambaradas profundas.",
    "ARMAF CLUB DE NUIT URBAN MAN ELIXIR EDP": "Elixir urbano masculino: notas verdes, madera y almizcle moderno.",
    "ARMAF CLUB DE NUIT WOMAN EDP":        "Chypre floral femenino con notas de grosella, rosa y almizcle.",
    "ARMAF CLUB DE NUYT MALEKA EDP":       "Real y femenino: floral oriental con rosa, oud y almizcle.",
    "ARMAF CONNOISSEUR MAN EDP":           "Amaderado aromático para el conocedor: cuero, cedro y almizcle.",
    "ARMAF CONNOISSEUR WOMAN EDP":         "Floral gourmand femenino con vainilla, iris y almizcle sedoso.",
    "ARMAF DELIGHTS ISLAND BLISS EDP":     "Tropical frutal: notas de coco, flor de tiaré y brisa marina.",
    "ARMAF DELIGHTS YUM YUM EDP":          "Dulce y adictivo: frutas tropicales, caramelo y almizcle suave.",
    "ARMAF ODYSSEY AOUD EDP":              "Oud árabe en clave moderna: resinas, madera y especias.",
    "ARMAF ODYSSEY BA HA MAS EDP":         "Caribeño y fresco: notas acuáticas, frutas tropicales y sándalo.",
    "ARMAF ODYSSEY BLACK FOREST EDP":      "Bosque oscuro: notas verdes, cedro, abeto y tierra húmeda.",
    "ARMAF ODYSSEY CANDEE EDP":            "Dulce como caramelo: vainilla, azúcar y notas de frutos rojos.",
    "ARMAF ODYSSEY DUBAI CHOCOLAT EDP":    "Indulgente: notas de chocolate de Dubái con oud y vainilla.",
    "ARMAF ODYSSEY HOMME EDP":             "Masculino aromático: notas verdes, madera y fondo especiado.",
    "ARMAF ODYSSEY HOMME WHITE INTENSE EDP": "Masculino fresco intenso: bergamota, vetiver y almizcle blanco.",
    "ARMAF ODYSSEY LIMONI EDP":            "Cítrico vibrante: limón siciliano, bergamota y base amaderada.",
    "ARMAF ODYSSEY MANDARIN SKY EDP":      "Cítrico aéreo: mandarina, notas florales y almizcle limpio.",
    "ARMAF ODYSSEY MANDARIN SKY ELIXIR EDP": "Versión intensa: mandarina concentrada, ámbar y madera.",
    "ARMAF ODYSSEY MARSHMALLOW EDP":       "Suave y nuboso: vainilla, almizcle blanco y notas de malvavisco.",
    "ARMAF ODYSSEY MEGA EDP":              "Potente amaderado oriental con oud, resinas y especias oscuras.",
    "ARMAF ODYSSEY REVOLUTION EDP":        "Revolucionario: notas de cuero, madera ahumada y ámbar.",
    "ARMAF ODYSSEY SPECTRA RAINBOW EDP":   "Arcoíris aromático: frutal floral con toques especiados y almizcle.",
    "ARMAF ODYSSEY TOFFEE COFFEE EDP":     "Gourmand irresistible: café, toffee y vainilla sobre madera.",
    "ARMAF ODYSSEY TYRANT EDP":            "Tiránico y oscuro: oud ahumado, cuero y notas especiadas.",

    # FOLIE PURE
    "FOLIE PURE 30ML EDP DESIREE":         "Deseable y coqueto: floral afrutado con notas de pera y jazmín.",
    "FOLIE PURE 30ML EDP DREAM DAYS":      "Días de ensueño: floral fresco con rosas, almizcle y notas suaves.",
    "FOLIE PURE 30ML EDP ELECTRIC LOVE":   "Amor eléctrico: frutal vibrante con bayas rojas y almizcle.",
    "FOLIE PURE 30ML EDP ESENCIA RAGIA":   "Oriental aromático con especias, oud y fondo de sándalo.",
    "FOLIE PURE 30ML EDP ETERNAL FLAME":   "Llama eterna: ámbar cálido, especias y notas amaderadas sensuales.",
    "FOLIE PURE 30ML EDP FASHION CLUB":    "De moda y moderno: floral cítrico con notas blancas y almizcle.",
    "FOLIE PURE 30ML EDP GREEN DREAM":     "Sueño verde: notas herbáceas, té verde y almizcle fresco.",
    "FOLIE PURE 30ML EDP LUXE ROUGE":      "Lujo rojo: floral intenso con rosas, frutos rojos y ámbar.",
    "FOLIE PURE 30ML EDP NEW FLOWER":      "Nueva flor: bouquet primaveral con lilas, muguet y almizcle.",
    "FOLIE PURE 30ML EDP PINK LIFE":       "Vida rosada: floral frutal con melocotón, rosa y vainilla suave.",
    "FOLIE PURE 30ML EDP PURPLE PEARL":    "Perla púrpura: floral afrutado con violeta, iris y almizcle.",
    "FOLIE PURE 30ML EDP VIP STREET":      "Urbano VIP: amaderado con cuero suave, almizcle y especias.",

    # FRENCH AVENUE
    "FRENCH AVENUE VENENO BIANCO EDP":     "Veneno blanco: floral oriental con jazmín, vainilla y almizcle.",
    "FRENCH AVENUE VENENO SCARLET EDP":    "Veneno escarlata: rosa intensa, frutos rojos y base ambarada.",
    "FRENCH AVENUE VULCAN BAIE EDP":       "Volcánico y fresco: bayas silvestres, ozono y notas amaderadas.",
    "FRENCH AVENUE VULCAN FEU EDP":        "Fuego volcánico: especias ardientes, oud y resinas oscuras.",

    # LATTAFA
    "LATTAFA 24 CARAT PURE GOLD EDP":      "Oro puro: oud lujoso, vainilla y rosas sobre base de ámbar dorado.",
    "LATTAFA 24 CARAT WHITE GOLD EDP":     "Oro blanco: floral limpio con almizcle blanco, sándalo y bergamota.",
    "LATTAFA AJWAD EDP":                   "Excelente: oud de calidad, incienso y notas especiadas cálidas.",
    "LATTAFA AJWAD PINK TO PINK EDP":      "Rosa a rosa: floral dulce con rosas, lichi y fondo ambarado.",
    "LATTAFA AL NASHAMA CAPRICE EDP":      "Caprichoso y elegante: floral ambarado con rosa y almizcle.",
    "LATTAFA AL NOBLE WAZEER EDP":         "Noble ministro: oud real, especias orientales y ámbar.",
    "LATTAFA AL NOLE SAFEER EDP":          "Embajador oriental: notas amaderadas, oud y especias reales.",
    "LATTAFA ANA ABIYEDH ROUGE EDP":       "Soy blanco y rojo: floral intenso con rosa y oud sobre ámbar.",
    "LATTAFA ASAD BOURBON EDP":            "León bourbon: notas ahumadas de bourbon, madera y cuero.",
    "LATTAFA ASAD EDP":                    "El León: amaderado intenso con notas de oud, cuero y especias.",
    "LATTAFA ASAD ELIXIR EDP":             "Elixir del León: versión concentrada con oud, ámbar y cuero.",
    "LATTAFA ASAD ZANZIBAR LIMITED EDITION EDP": "Zanzibar: especias exóticas de la isla, oud y notas tropicales.",
    "LATTAFA ASDAAF AMEERAT AL ARAB EDP":  "Princesa de Arabia: floral oriental con rosa, oud y almizcle.",
    "LATTAFA ASDAAF AMEERAT AL ARAB PRIVE ROSE EDP": "Rosa privada de princesa: rosa turca intensa y almizcle suave.",
    "LATTAFA ASDAAF AMEER AL ARAB EDP":    "Príncipe árabe: oud real, incienso y notas especiadas nobles.",
    "LATTAFA ASDAAF AMEER AL ARAB IMPERIUM EDP": "Imperio: oud imperial, especias y fondo de ámbar y cuero.",
    "LATTAFA ASDAAF ANDALEEB EDP":         "El ruiseñor: floral frutal con notas de melocotón, rosa y vainilla.",
    "LATTAFA ASDAAF ANDALEEB FLORA EDP":   "Flora del ruiseñor: primaveral con flores blancas y fondo de ámbar.",
    "LATTAFA ATHEERI EDP":                 "Espectral: notas aéreas de sándalo, almizcle y flores blancas.",
    "LATTAFA BADE'E AL OUD AMETHYST EDP":  "Oud amatista: oud floral con violeta, ámbar y notas especiadas.",
    "LATTAFA BADE'E AL OUD HONOR GLORY EDP": "Honor y gloria: oud imponente, incienso y resinas reales.",
    "LATTAFA BADE'E AL OUD NOBLE BLUSH EDP": "Oud noble rosado: rosa, oud suave y notas de almizcle.",
    "LATTAFA BADE'E AL OUD OUD FOR GLORY EDP": "Oud para la gloria: puro y poderoso con especias y resinas.",
    "LATTAFA BADE'E AL OUD SUBLIME EDP":   "Oud sublime: refinado y elegante con notas florales y ámbar.",
    "LATTAFA CONFIDENTIAL PRIVATE PLATINUM EDP": "Platino privado: amaderado exclusivo con especias y almizcle.",
    "LATTAFA ECLAIRE BANOFFI EDP":         "Éclair banoffee: gourmand con caramelo, plátano y vainilla.",
    "LATTAFA ECLAIRE EDP":                 "Éclair: dulce y tentador, notas de vainilla y crema pastelera.",
    "LATTAFA ECLAIRE PISTACHE EDP":        "Éclair pistacho: gourmand verde con pistacho, vainilla y almizcle.",
    "LATTAFA EJAAZI EDP":                  "Milagroso: floral oriental con rosa, azafrán y base de oud.",
    "LATTAFA EMEER EDP":                   "El Emir: oud especiado real con notas de cuero y ámbar.",
    "LATTAFA FAKHAR EXTRAIT EDP":          "Orgullo en extrait: oud concentrado, azafrán y rosas.",
    "LATTAFA FAKHAR PLATIN EDP":           "Orgullo platino: amaderado lujoso con oud, platino y especias.",
    "LATTAFA FAKHAR WOMEN EDP":            "Orgullo femenino: floral oriental con rosa, oud y ámbar suave.",
    "LATTAFA HABIK EDP":                   "Tu amor: romántico y floral con rosas, almizcle y vainilla.",
    "LATTAFA HAYAATI AL MALEKY EDP":       "Mi vida real: oud real, incienso y notas de azafrán.",
    "LATTAFA HAYAATI FLORENCE EDP":        "Mi vida en Florencia: floral italiano con iris, rosa y notas verdes.",
    "LATTAFA HAYAATI GOLD EDP":            "Mi vida dorada: oud, vainilla y rosas sobre ámbar dorado.",
    "LATTAFA HER CONFESSION EDP":          "Su confesión: floral frutal con fresas, rosas y almizcle dulce.",
    "LATTAFA HIS CONFESSION EDP":          "Su confesión masculina: amaderado aromático con especias y cuero.",
    "LATTAFA KHAMRAH DUKHAN EDP":          "Vino ahumado: incienso y oud ahumado sobre notas especiadas.",
    "LATTAFA KHAMRAH EDP":                 "El vino: oriental especiado con oud, canela y notas vinosas.",
    "LATTAFA KHAMRAH QAHWA EDP":           "Vino y café: oud árabe con notas de café y especias orientales.",
    "LATTAFA KING OF ARABIA EDP":          "Rey de Arabia: oud majestuoso, incienso y especias imperiales.",
    "LATTAFA LAIL MALEKI EDP":             "Mi noche real: nocturno con oud oscuro, rosas y almizcle.",
    "LATTAFA MAAHIR BLACK EDP":            "Maestro negro: oud intenso, ahumado y cuero sobre ámbar oscuro.",
    "LATTAFA MAAHIR EDP":                  "El maestro: amaderado especiado con oud, sándalo y almizcle.",
    "LATTAFA MAAHIR LEGACY EDP":           "Legado maestro: herencia aromática con oud, rosas y especias.",
    "LATTAFA MAYAR CHERRY INTENSE EDP":    "Cereza intensa: frutal vibrante con cereza negra y almizcle.",
    "LATTAFA MAYAR EDP":                   "Mayar: floral frutal con frutos rojos, jazmín y vainilla.",
    "LATTAFA MAYAR NATURAL INTENSE EDP":   "Natural intenso: frutal amaderado con bayas y base de ámbar.",
    "LATTAFA MUSAMAM WHITE INTENSE EDP":   "Blanco intenso: almizcle puro, flores blancas y sándalo.",
    "LATTAFA PETRA EDP":                   "Petra: piedra arenisca, rosas del desierto y notas especiadas.",
    "LATTAFA PRIDE AL QIAM GOLD EDP":      "Valor dorado: oud de lujo, azafrán y rosas sobre ámbar.",
    "LATTAFA PRIDE AL QIAM SILVER EDP":    "Valor plateado: fresco amaderado con bergamota y almizcle.",
    "LATTAFA PRIDE ANSAAM GOLD EDP":       "Armonía dorada: floral oriental con rosa, oud y especias.",
    "LATTAFA PRIDE ANSAAM SILVER EDP":     "Armonía plateada: fresco floral con notas cítricas y almizcle.",
    "LATTAFA PRIDE ART OF UNIVERSE EDP":   "Arte del universo: cósmico y profundo con oud y resinas.",
    "LATTAFA PRIDE ISHQ AL SHUYUKH GOLD EDP": "Amor de los jeques: oud real, azafrán y rosas doradas.",
    "LATTAFA PRIDE LA COLLECTION D'ANTIQUITES 1910 EDP": "1910: vintage con notas de cuero, iris y sándalo clásico.",
    "LATTAFA PRIDE NEBRAS EDP":            "La luz: floral luminoso con jazmín, almizcle y notas cítricas.",
    "LATTAFA PRIDE NEBRAS ELIXIR EDP":     "Elixir de luz: versión concentrada con jazmín y ámbar.",
    "LATTAFA PRIDE SHAHEEN GOLD EDP":      "Halcón dorado: especiado amaderado con oud y azafrán.",
    "LATTAFA PRIDE SHAHEEN SILVER EDP":    "Halcón plateado: fresco masculino con especias y madera.",
    "LATTAFA QAED AL FURSAN EDP":          "Líder de los caballeros: amaderado noble con cuero y oud.",
    "LATTAFA QAED AL FURSAN UNLIMITED EDP": "Sin límites: expansivo, amaderado con notas frescas y cuero.",
    "LATTAFA QAED AL FURSAN UNTAMED EDP":  "Indomable: salvaje y especiado con cuero oscuro y oud.",
    "LATTAFA QIMMAH FOR MEN EDP":          "Valor masculino: amaderado intenso con especias y almizcle.",
    "LATTAFA QIMMAH FOR WOMEN EDP":        "Valor femenino: floral suave con rosas, almizcle y vainilla.",
    "LATTAFA SAKEENA EDP":                 "Serenidad: tranquilo y floral con notas blancas y almizcle puro.",
    "LATTAFA TERIAQ INTENSE EDP":          "Triaca intensa: oud medicinal, especias y notas de incienso.",
    "LATTAFA THE KINGDOM MAN EDP":         "El Reino masculino: oud poderoso, especias y notas amaderadas.",
    "LATTAFA THE KINGDOM WOMAN EDP":       "El Reino femenino: floral oriental con rosas, oud y almizcle.",
    "LATTAFA VICTORIA EDP":                "Victoria: floral elegante con rosas, violeta y ámbar suave.",
    "LATTAFA YARA CANDY EDP":              "Yara dulce: gourmand con frutos del bosque, azúcar y almizcle.",
    "LATTAFA YARA EDP":                    "Frutal floral femenino con pera, melocotón y rosas sobre almizcle.",
    "LATTAFA YARA ELIXIR EDP":             "Elixir de Yara: concentrado frutal floral, intenso y duradero.",
    "LATTAFA YARA MOI EDP":                "Yara para mí: versión suave con flores blancas y almizcle.",
    "LATTAFA YARA TOUS EDP":               "Yara para todas: frutal universal con notas cítricas y florales.",

    # MAISON ALHAMBRA
    "MAISON ALHAMBRA ALPINE HOMME SPORT EDP":       "Deportivo alpino: notas acuáticas, menta y fondo amaderado.",
    "MAISON ALHAMBRA CHANTS TENDERINA EDP":          "Ternura cantada: floral suave con magnolia, almizcle y ámbar.",
    "MAISON ALHAMBRA EXQUISITE CLUB POUR HOMME EDP": "Club exquisito: notas de tabaco, madera y especias orientales.",
    "MAISON ALHAMBRA GALACTIC MEN ELIXIR EDP":       "Elixir galáctico: amaderado profundo con notas de oud y especias.",
    "MAISON ALHAMBRA GALACTIC MEN INTENSE EDP":      "Masculino intenso: notas cítricas, especias y base de madera.",
    "MAISON ALHAMBRA INFINI INTOXICATING CHERRY EDP": "Cereza embriagadora: frutal adictivo con cereza, vainilla y ámbar.",
    "MAISON ALHAMBRA INTRUDE EDP":                   "Intrusión: fresco amaderado con notas acuáticas y almizcle.",
    "MAISON ALHAMBRA JEAN LOWE IMMORTEL EDP":        "Inmortal: amaderado eterno con oud, sándalo y resinas.",
    "MAISON ALHAMBRA JORGE DI PROFUMO AQUA EDP":     "Aqua: fresco marino con notas cítricas y fondo amaderado.",
    "MAISON ALHAMBRA JORGE DI PROFUMO DEEP BLUE EDP": "Azul profundo: acuático intenso con especias y madera oscura.",
    "MAISON ALHAMBRA JORGE DI PROFUMO EDP":          "Amaderado elegante con notas de bergamota, vetiver y almizcle.",
    "MAISON ALHAMBRA LA ROUGE BAROQUE EDP":          "Barroco rojo: floral intenso con rosas, incienso y ámbar.",
    "MAISON ALHAMBRA LA ROUGE BAROQUE EXTREME EDP":  "Barroco extremo: máxima intensidad con oud, rosas y especias.",
    "MAISON ALHAMBRA LA VIVACITE INTENSA EDP":        "Vivacidad intensa: floral cítrico vibrante con rosas y bergamota.",
    "MAISON ALHAMBRA LA VOIE EDP":                   "El camino: floral elegante con iris, rosas y almizcle puro.",
    "MAISON ALHAMBRA LUXE BOLD EDP":                 "Lujo audaz: oud oscuro, cuero y notas especiadas opulentas.",
    "MAISON ALHAMBRA NO.2 MEN EDP":                  "N.2 masculino: fougère clásico con lavanda, cedro y almizcle.",
    "MAISON ALHAMBRA PHILOS CENTRO EDP":             "Centro filosófico: amaderado equilibrado con notas de especias.",
    "MAISON ALHAMBRA PHILOS OPUS NOIR EDP":          "Opus negro: oud oscuro, incienso y rosas sobre ámbar.",
    "MAISON ALHAMBRA PHILOS SHINE EDP":              "Brillo filosófico: floral luminoso con notas cítricas y almizcle.",
    "MAISON ALHAMBRA REYNA POUR FEMME EDP":          "Reina femenina: floral opulento con rosas, iris y vainilla.",
    "MAISON ALHAMBRA ROSE ORIGAMI EDP":              "Rosa origami: floral artístico con rosa, almizcle y notas verdes.",
    "MAISON ALHAMBRA ROSE SEDUCTION VIP POUR FEMME EDP": "Seducción VIP: rosa intensa, almizcle y fondo de ámbar.",
    "MAISON ALHAMBRA SO CANDID POUR FEMME EDP":      "Tan sincera: floral transparente con flores blancas y almizcle.",
    "MAISON ALHAMBRA VICTORIOSO EDP":                "Victorioso: amaderado masculino con notas especiadas y cuero.",
    "MAISON ALHAMBRA VICTORIOSO NERO EDP":           "Victorioso negro: oud ahumado, cuero y especias oscuras.",
    "MAISON ALHAMBRA YEAH! MAN EDP":                 "¡Sí! masculino: fresco vibrante con cítricos, especias y madera.",
    "MAISON ALHAMBRA YEAH! MAN PARFUM EDP":          "¡Sí! en parfum: versión intensa con oud, especias y madera.",

    # ORIENTICA
    "ORIENTICA ROYAL AMBER EDP":           "Ámbar real: opulento y rico con oud, vainilla y especias doradas.",

    # RASASI HAWAS
    "RASASI HAWAS BLACK EDP":              "Hawas negro: fougère oscuro con notas verdes y madera ahumada.",
    "RASASI HAWAS DIVA EDP":               "Diva: floral frutal femenino con fresas, rosas y almizcle.",
    "RASASI HAWAS FOR HIM EDP":            "Para él: fougère fresco con lavanda, menta y base amaderada.",
    "RASASI HAWAS ICE EDP":                "Hielo: ultra fresco con notas heladas de menta y cítricos.",
    "RASASI HAWAS MALIBU EDP":             "Malibu: playero tropical con coco, frutas y notas marinas.",
    "RASASI HAWAS TROPICAL EDP":           "Tropical: frutal exótico con mango, maracuyá y notas florales.",

    # RAYHAAN
    "RAYHAAN OCEAN RUSH EDP":              "Prisa oceánica: marino intenso con notas acuáticas y almizcle.",

    # XERJOFF
    "XERJOFF ERBA PURA EDP":               "Hierba pura: cítrico frutal con mandarina, frutas blancas y almizcle.",

    # ZIMAYA
    "ZIMAYA FATIMA PINK EXTRAIT DE PARFUM": "Fátima rosada: floral opulento en extrait con rosas y oud suave.",
    "ZIMAYA TIRAMISU CARAMEL EDP":          "Tiramisú caramelo: gourmand dulce con café, caramelo y vainilla.",
    "ZIMAYA TIRAMISU COCO EDP":             "Tiramisú coco: exótico con coco, café y notas cremosas.",

    # BODY CREAMS
    "BODY CREAM AFEER AL NOBLE WAZEER":    "Notas amaderadas y especiadas con oud y ámbar.",
    "BODY CREAM AFEER ANGEL":              "Dulce y celestial con vainilla, almizcle y flores blancas.",
    "BODY CREAM AFEER ASAD":               "Masculino y amaderado con notas de oud y cuero.",
    "BODY CREAM AFEER DELILAH":            "Seductor floral con rosas, sándalo y almizcle suave.",
    "BODY CREAM AFEER FAKHAR MAN":         "Orgulloso masculino con especias orientales y madera.",
    "BODY CREAM AFEER FAKHAR WOMEN":       "Orgulloso femenino con rosas, oud y vainilla.",
    "BODY CREAM AFEER MUSAMAM WHITE INTENSE": "Blanco intenso: almizcle puro y flores blancas.",
    "BODY CREAM AFEER NUIT ROYALE INTENSE MAN": "Noche real masculina: oscuro y especiado con oud.",
    "BODY CREAM AFEER NUIT ROYALE WOMAN":  "Noche real femenina: floral con rosas y almizcle.",
    "BODY CREAM AFEER ROYAL AMBER":        "Ámbar real: cálido con ámbar, vainilla y sándalo.",
    "BODY CREAM AFEER SABAH AL WARD":      "Mañana de rosas: fresco floral con rosas y almizcle.",
    "BODY CREAM AFEER YARA":               "Frutal floral con pera y rosas sobre almizcle suave.",
    "BODY CREAM ANWAR ANGEL":              "Ángel: dulce y sedoso con vainilla y flores blancas.",
    "BODY CREAM ANWAR ASAD":               "Amaderado y especiado con notas de oud.",
    "BODY CREAM ANWAR DELILAH":            "Floral seductor con rosas, jazmín y almizcle.",
    "BODY CREAM ANWAR ELLY ABALI":         "Oriental especiado con ámbar y resinas.",
    "BODY CREAM ANWAR FAKHAR MAN":         "Masculino oriental con especias y madera.",
    "BODY CREAM ANWAR FAKHAR WOMEN":       "Femenino oriental con rosas y ámbar.",
    "BODY CREAM ANWAR MUSAMAM WHITE INTENSE": "Almizcle blanco puro y flores.",
    "BODY CREAM ANWAR NUIT ROYALE INTENSE MAN": "Noche intensa con oud y especias.",
    "BODY CREAM ANWAR NUIT ROYALE WOMAN":  "Noche floral con rosas y almizcle.",
    "BODY CREAM ANWAR ROYAL AMBER":        "Ámbar cálido con vainilla y sándalo.",
    "BODY CREAM ANWAR SABAH AL WARD":      "Rosa fresca de la mañana.",
    "BODY CREAM ANWAR YARA":               "Frutal floral con pera y rosas.",
    "BODY CREAM KARSEELL ARGAN OIL":       "Nutritiva con aceite de argán marroquí y notas florales.",
    "BODY CREAM KARSEELL COLLAGEN":        "Reafirmante con colágeno y aroma suave de vainilla.",
    "BODY CREAM KARSEELL HAIR MASK":       "Mascarilla reparadora con aceites naturales y aroma suave.",
    "BODY CREAM LATTAFA ASAD":             "Amaderado y cuero con notas de oud.",
    "BODY CREAM LATTAFA OUD MOOD":         "Oud aromático con especias orientales.",
    "BODY CREAM LATTAFA QAED AL FURSAN":   "Noble y amaderado con notas de oud y cuero.",
    "BODY CREAM LATTAFA QIMMAH":           "Oriental especiado con ámbar y rosas.",
    "BODY CREAM LATTAFA YARA":             "Frutal floral con pera y almizcle suave.",
    "BODY CREAM VICTORIA'S SECRET LOVE SPELL": "Hechizo de amor: frutal floral con cereza y durazno.",
    "BODY CREAM VICTORIA'S SECRET PURE SEDUCTION": "Pura seducción: frutal floral con uva y manzana.",
    "BODY CREAM VICTORIA'S SECRET VELVET PETALS": "Pétalos de terciopelo: floral suave con rosa y sándalo.",

    # AMBIENTADORES
    "AMBIENTADOR LATTAFA AMEERAT AL ARAB AIR FRESHENER": "Princesa árabe: floral oriental con rosa, oud y almizcle.",
    "AMBIENTADOR LATTAFA KHAMRAH AIR FRESHENER":         "Oriental especiado con notas de oud, canela y ámbar.",
}

# ─── Fallback por keywords en el nombre ───
def aroma_por_keywords(nombre, categoria):
    n = nombre.upper()

    if categoria == "Ambientadores":
        return "Fragancia de ambiente inspirada en perfumería árabe de lujo."

    if categoria == "Body Cream":
        if "ARGAN" in n:      return "Nutritiva con aceite de argán y aroma floral suave."
        if "COLLAGEN" in n:   return "Reafirmante con aroma fresco y suave."
        if "HAIR" in n:       return "Mascarilla de cabello con aceites naturales aromáticos."
        if "AMBER" in n or "AMBRE" in n: return "Ámbar cálido con vainilla y notas amaderadas."
        if "ROSE" in n or "WARD" in n: return "Floral con rosas y almizcle suave."
        if "YARA" in n:       return "Frutal floral con pera y rosas sobre almizcle."
        if "OUD" in n:        return "Oud aromático y especiado."
        if "WHITE" in n:      return "Almizcle blanco y flores limpias."
        if "MUSK" in n:       return "Almizcle sedoso y suave."
        if "ANGEL" in n:      return "Celestial: vainilla, almizcle y flores blancas."
        if "ROYAL" in n:      return "Oriental especiado con notas reales."
        if "NUIT" in n or "NIGHT" in n: return "Nocturno y misterioso con especias y oud."
        return "Crema corporal perfumada con fragancia oriental."

    # Perfumes — por keywords
    pairs = [
        (["AMBER OUD", "AMBRE OUD"],  "Ámbar y oud: cálido, profundo y especiado."),
        (["OUD FOR GLORY", "OUD MOOD"], "Oud puro y poderoso con notas resinosas."),
        (["OUD"],                      "Oud árabe con notas amaderadas y especiadas."),
        (["AMBER", "AMBRE", "AMBAR"], "Ámbar cálido con vainilla y notas orientales."),
        (["ROSE", "WARD", "ROSA"],    "Floral elegante con rosas frescas y almizcle suave."),
        (["CHERRY", "CEREZA"],        "Frutal vibrante con cereza y notas dulces."),
        (["CITRUS", "LIMONI", "CITRIC", "MANDARIN", "BERGAMOT"], "Cítrico fresco y energizante."),
        (["AQUA", "OCEAN", "MARINE", "TROPICAL", "BEACH"], "Fresco acuático con notas marinas."),
        (["GOLD", "GOLDEN", "DORADO", "24 CARAT"], "Lujoso y dorado con oud, vainilla y especias."),
        (["SILVER", "PLATINUM", "PLATIN", "PLATINO"], "Fresco y limpio con notas amaderadas plateadas."),
        (["COFFEE", "CAFE", "QAHWA", "TOFFEE"],       "Gourmand con notas de café y especias cálidas."),
        (["CHOCOLATE", "CHOCO"],      "Gourmand irresistible con notas de chocolate y vainilla."),
        (["VANILLA", "VAINILLA"],     "Dulce y cremoso con vainilla y almizcle."),
        (["MUSK", "ALMIZCLE"],        "Almizcle puro, suave y envolvente."),
        (["SPORT", "ICE", "FRESCO"],  "Fresco deportivo con notas acuáticas y cítricas."),
        (["NIGHT", "NOIR", "BLACK", "DARK", "NUIT", "LAIL"], "Nocturno y oscuro: oud ahumado y especias."),
        (["SANDALWOOD", "SANDALO"],   "Sándalo cremoso y cálido sobre almizcle."),
        (["INCENSE", "INCIENSO", "DUKHAN", "BAKHOOR"], "Incienso ahumado con resinas y especias."),
        (["SPICE", "SPICY", "ESPECIAS", "CANELA", "CINNAMON"], "Especiado cálido con canela y cardamomo."),
        (["LEATHER", "CUERO"],        "Cuero refinado con notas amaderadas y especiadas."),
        (["FLORAL", "FLOWER", "FLORA", "BLOOM"], "Floral elegante con notas de jazmín y rosas."),
        (["FRUITY", "FRUIT", "FRUTA", "BERRY", "BAIE"], "Frutal vibrante con bayas y notas florales."),
        (["GREEN", "VERDE", "HERBAL"], "Verde y fresco con notas herbáceas y madera."),
        (["SWEET", "DULCE", "CANDY", "SUGAR"], "Dulce y adictivo con notas gourmand."),
    ]

    for keywords, desc in pairs:
        for kw in keywords:
            if kw in n:
                return desc

    # Fallback genérico por marca
    if "LATTAFA" in n:   return "Oriental árabe con notas amaderadas y especiadas."
    if "ARMAF" in n:     return "Amaderado especiado de inspiración oriental."
    if "RASASI" in n:    return "Fragancia árabe de alta perfumería."
    if "AL HARAMAIN" in n: return "Oriental lujoso con oud y ámbar puro."
    if "MAISON ALHAMBRA" in n: return "Amaderado elegante de inspiración francesa."
    if "FOLIE PURE" in n: return "Fragrance francés ligero y femenino."
    if "ZIMAYA" in n:    return "Oriental gourmand con notas dulces y especiadas."
    if "ORIENTICA" in n: return "Oriental opulento con oud y especias."
    if "XERJOFF" in n:   return "Fragancia de nicho: cítrico frutal con almizcle."

    return "Fragancia oriental de alta perfumería árabe."


# ─── Aplicar descripciones ───
with open('focus-web/js/catalogo.js', 'r', encoding='utf-8') as f:
    content = f.read()
products = json.loads(content[len('const CATALOGO = '):-1])

sin_desc = 0
for p in products:
    nombre_clave = re.sub(r'^(PERFUME|BODY CREAM|AMBIENTADOR)\s+', '', p['nombre']).strip()
    if nombre_clave in ESPECIFICOS:
        p['aroma'] = ESPECIFICOS[nombre_clave]
    else:
        # Try full name too
        if p['nombre'] in ESPECIFICOS:
            p['aroma'] = ESPECIFICOS[p['nombre']]
        else:
            p['aroma'] = aroma_por_keywords(p['nombre'], p['categoria'])
            sin_desc += 1

with open('focus-web/js/catalogo.js', 'w', encoding='utf-8') as f:
    f.write('const CATALOGO = ' + json.dumps(products, ensure_ascii=False, indent=2) + ';')

# Stats
from collections import Counter
def tipo(p):
    clave = re.sub(r'^(PERFUME|BODY CREAM|AMBIENTADOR)\s+', '', p['nombre']).strip()
    return 'especifico' if clave in ESPECIFICOS else 'keyword'
tipos = Counter(tipo(p) for p in products)
print('Total:', len(products), 'productos')
print('Con descripcion especifica:', tipos['especifico'])
print('Con descripcion por keyword/fallback:', tipos['keyword'])
print()
print('Muestra:')
for p in products[:5]:
    print(' ', p['nombre'][:50], ':', p['aroma'])
