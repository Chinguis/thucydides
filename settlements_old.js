// Ancient Greek settlements data with their approximate coordinates
// Names are given in English translation of the ancient Greek names
const settlements = [
    // Greece Mainland
    { name: 'Athens', modern: 'Athens', lat: 37.9838, lng: 23.7275, type: 'Major Polis' },
    { name: 'Sparta', modern: 'Sparta', lat: 37.0810, lng: 22.4300, type: 'Major Polis' },
    { name: 'Thebes', modern: 'Thebes', lat: 38.3250, lng: 23.3189, type: 'Major Polis' },
    { name: 'Corinth', modern: 'Corinth', lat: 37.9065, lng: 22.8790, type: 'Major Polis' },
    { name: 'Argos', modern: 'Argos', lat: 37.6333, lng: 22.7286, type: 'Polis' },
    { name: 'Megara', modern: 'Megara', lat: 38.0000, lng: 23.3433, type: 'Polis' },
    { name: 'Olympia', modern: 'Olympia', lat: 37.6379, lng: 21.6300, type: 'Sanctuary' },
    { name: 'Delphi', modern: 'Delphi', lat: 38.4824, lng: 22.5010, type: 'Sanctuary' },
    { name: 'Epidaurus', modern: 'Epidaurus', lat: 37.5960, lng: 23.0789, type: 'Sanctuary' },
    { name: 'Messene', modern: 'Messene', lat: 37.1833, lng: 21.9167, type: 'Polis' },
    { name: 'Pylos', modern: 'Pylos', lat: 36.9133, lng: 21.6969, type: 'Settlement' },
    { name: 'Mantinea', modern: 'Mantinea', lat: 37.5928, lng: 22.4039, type: 'Polis' },
    { name: 'Elis', modern: 'Elis', lat: 37.7333, lng: 21.3333, type: 'Polis' },
    { name: 'Sicyon', modern: 'Sicyon', lat: 37.9833, lng: 22.7167, type: 'Polis' },
    { name: 'Troezen', modern: 'Troezen', lat: 37.5217, lng: 23.3756, type: 'Polis' },

    // Northern Greece
    { name: 'Thessalonica', modern: 'Thessaloniki', lat: 40.6401, lng: 22.9444, type: 'Settlement' },
    { name: 'Pella', modern: 'Pella', lat: 40.7619, lng: 22.5253, type: 'Polis' },
    { name: 'Amphipolis', modern: 'Amphipolis', lat: 40.8217, lng: 23.8469, type: 'Polis' },
    { name: 'Potidaea', modern: 'Potidaea', lat: 40.2000, lng: 23.3333, type: 'Polis' },
    { name: 'Olynthus', modern: 'Olynthus', lat: 40.2981, lng: 23.3508, type: 'Polis' },
    { name: 'Larissa', modern: 'Larissa', lat: 39.6390, lng: 22.4190, type: 'Polis' },
    { name: 'Pherae', modern: 'Pherae', lat: 39.4667, lng: 22.4667, type: 'Polis' },

    // Islands - Aegean
    { name: 'Delos', modern: 'Delos', lat: 37.3964, lng: 25.2683, type: 'Sanctuary' },
    { name: 'Naxos', modern: 'Naxos', lat: 37.1036, lng: 25.3764, type: 'Polis' },
    { name: 'Paros', modern: 'Paros', lat: 37.0850, lng: 25.1486, type: 'Polis' },
    { name: 'Samos', modern: 'Samos', lat: 37.7558, lng: 26.9775, type: 'Polis' },
    { name: 'Chios', modern: 'Chios', lat: 38.3678, lng: 26.1361, type: 'Polis' },
    { name: 'Lesbos', modern: 'Lesbos', lat: 39.1000, lng: 26.3333, type: 'Island' },
    { name: 'Mytilene', modern: 'Mytilene', lat: 39.1083, lng: 26.5583, type: 'Polis' },
    { name: 'Rhodes', modern: 'Rhodes', lat: 36.4341, lng: 28.2176, type: 'Polis' },
    { name: 'Cos', modern: 'Kos', lat: 36.8933, lng: 27.2881, type: 'Polis' },
    { name: 'Thasos', modern: 'Thasos', lat: 40.7772, lng: 24.7092, type: 'Polis' },

    // Crete
    { name: 'Cnossus', modern: 'Knossos', lat: 35.2980, lng: 25.1630, type: 'Settlement' },
    { name: 'Gortyn', modern: 'Gortyn', lat: 35.0628, lng: 24.9489, type: 'Polis' },
    { name: 'Cydonia', modern: 'Chania', lat: 35.5138, lng: 24.0180, type: 'Polis' },

    // Asia Minor (Ionia)
    { name: 'Miletus', modern: 'Miletus', lat: 37.5333, lng: 27.2833, type: 'Major Polis' },
    { name: 'Ephesus', modern: 'Ephesus', lat: 37.9395, lng: 27.3408, type: 'Major Polis' },
    { name: 'Halicarnassus', modern: 'Halicarnassus', lat: 37.0379, lng: 27.4241, type: 'Polis' },
    { name: 'Smyrna', modern: 'Izmir', lat: 38.4192, lng: 27.1287, type: 'Polis' },
    { name: 'Pergamum', modern: 'Pergamon', lat: 39.1319, lng: 27.1844, type: 'Polis' },
    { name: 'Sardis', modern: 'Sardis', lat: 38.4881, lng: 28.0392, type: 'Polis' },
    { name: 'Phocaea', modern: 'Phocaea', lat: 38.6667, lng: 26.7667, type: 'Polis' },
    { name: 'Colophon', modern: 'Colophon', lat: 38.0667, lng: 27.2833, type: 'Polis' },
    { name: 'Priene', modern: 'Priene', lat: 37.6583, lng: 27.2972, type: 'Polis' },

    // Black Sea Region
    { name: 'Byzantium', modern: 'Istanbul', lat: 41.0082, lng: 28.9784, type: 'Major Polis' },
    { name: 'Sinope', modern: 'Sinop', lat: 42.0264, lng: 35.1531, type: 'Polis' },
    { name: 'Trapezus', modern: 'Trabzon', lat: 41.0027, lng: 39.7168, type: 'Polis' },
    { name: 'Heraclea Pontica', modern: 'Ereğli', lat: 41.2833, lng: 31.4167, type: 'Polis' },

    // Sicily and Southern Italy (Magna Graecia)
    { name: 'Syracuse', modern: 'Syracuse', lat: 37.0755, lng: 15.2866, type: 'Major Polis' },
    { name: 'Acragas', modern: 'Agrigento', lat: 37.3119, lng: 13.5766, type: 'Major Polis' },
    { name: 'Gela', modern: 'Gela', lat: 37.0667, lng: 14.2500, type: 'Polis' },
    { name: 'Selinus', modern: 'Selinunte', lat: 37.5833, lng: 12.8333, type: 'Polis' },
    { name: 'Himera', modern: 'Himera', lat: 37.9736, lng: 13.8164, type: 'Polis' },
    { name: 'Tarentum', modern: 'Taranto', lat: 40.4761, lng: 17.2303, type: 'Major Polis' },
    { name: 'Croton', modern: 'Crotone', lat: 39.0806, lng: 17.1250, type: 'Polis' },
    { name: 'Sybaris', modern: 'Sybaris', lat: 39.7333, lng: 16.5000, type: 'Polis' },
    { name: 'Rhegium', modern: 'Reggio Calabria', lat: 38.1080, lng: 15.6435, type: 'Polis' },
    { name: 'Locri', modern: 'Locri', lat: 38.2333, lng: 16.2667, type: 'Polis' },
    { name: 'Neapolis', modern: 'Naples', lat: 40.8518, lng: 14.2681, type: 'Polis' },
    { name: 'Poseidonia', modern: 'Paestum', lat: 40.4200, lng: 15.0050, type: 'Polis' },

    // Cyrenaica (North Africa)
    { name: 'Cyrene', modern: 'Cyrene', lat: 32.8250, lng: 21.8583, type: 'Major Polis' },
    { name: 'Barca', modern: 'Barce', lat: 32.4000, lng: 20.8333, type: 'Polis' },

    // Thrace and Northern Aegean
    { name: 'Abdera', modern: 'Abdera', lat: 40.9456, lng: 24.9789, type: 'Polis' },
    { name: 'Maronea', modern: 'Maroneia', lat: 40.8642, lng: 25.5286, type: 'Polis' },

    // Epirus
    { name: 'Dodona', modern: 'Dodona', lat: 39.5478, lng: 20.7847, type: 'Sanctuary' },
    { name: 'Ambracia', modern: 'Arta', lat: 39.1608, lng: 20.9858, type: 'Polis' },

    // Cyprus
    { name: 'Salamis', modern: 'Salamis', lat: 35.1833, lng: 33.9000, type: 'Polis' },
    { name: 'Citium', modern: 'Larnaca', lat: 34.9167, lng: 33.6333, type: 'Polis' },

    // Additional Important Sites
    { name: 'Thermopylae', modern: 'Thermopylae', lat: 38.7967, lng: 22.5369, type: 'Pass' },
    { name: 'Marathon', modern: 'Marathon', lat: 38.1542, lng: 23.9633, type: 'Settlement' },
    { name: 'Plataea', modern: 'Plataea', lat: 38.2167, lng: 23.2833, type: 'Polis' },
    { name: 'Aegina', modern: 'Aegina', lat: 37.7500, lng: 23.4333, type: 'Polis' },

    // Key locations from Thucydides - Western Greece and Ionian Islands
    { name: 'Epidamnus', modern: 'Durrës', lat: 41.3275, lng: 19.8187, type: 'Major Polis' },
    { name: 'Corcyra', modern: 'Corfu', lat: 39.6243, lng: 19.9217, type: 'Major Polis' },
    { name: 'Naupactus', modern: 'Nafpaktos', lat: 38.3917, lng: 21.8281, type: 'Polis' },
    { name: 'Leucas', modern: 'Lefkada', lat: 38.8333, lng: 20.7069, type: 'Polis' },
    { name: 'Zacynthus', modern: 'Zakynthos', lat: 37.7869, lng: 20.8986, type: 'Polis' },
    { name: 'Cephallenia', modern: 'Kefalonia', lat: 38.1753, lng: 20.5689, type: 'Island' },
    { name: 'Anactorium', modern: 'Actium', lat: 38.9500, lng: 20.9167, type: 'Polis' },
    { name: 'Stratus', modern: 'Stratos', lat: 38.7667, lng: 21.3000, type: 'Polis' },
    { name: 'Oeniadae', modern: 'Oeniadae', lat: 38.4333, lng: 21.2000, type: 'Polis' },
    { name: 'Sollium', modern: 'Sollion', lat: 38.9000, lng: 20.8833, type: 'Fort' },
    { name: 'Astacus', modern: 'Astakos', lat: 38.5333, lng: 21.0833, type: 'Settlement' },

    // Attica and Attic Fortresses
    { name: 'Decelea', modern: 'Decelea', lat: 38.1000, lng: 23.8833, type: 'Fort' },
    { name: 'Oropus', modern: 'Oropos', lat: 38.3333, lng: 23.7667, type: 'Settlement' },
    { name: 'Oenoe', modern: 'Oenoe', lat: 38.2833, lng: 23.5833, type: 'Fort' },
    { name: 'Panactum', modern: 'Panactum', lat: 38.2667, lng: 23.4500, type: 'Fort' },
    { name: 'Phyle', modern: 'Phyle', lat: 38.1333, lng: 23.6667, type: 'Fort' },
    { name: 'Eleusis', modern: 'Elefsina', lat: 38.0406, lng: 23.5392, type: 'Sanctuary' },
    { name: 'Acharnae', modern: 'Acharnes', lat: 38.0833, lng: 23.7333, type: 'Deme' },

    // Megaris
    { name: 'Nisaea', modern: 'Nisaea', lat: 37.9667, lng: 23.3833, type: 'Port' },
    { name: 'Pegae', modern: 'Pegae', lat: 38.1667, lng: 23.0833, type: 'Port' },
    { name: 'Minoa', modern: 'Minoa', lat: 37.9333, lng: 23.4000, type: 'Fort' },

    // Boeotia
    { name: 'Tanagra', modern: 'Tanagra', lat: 38.3333, lng: 23.5667, type: 'Polis' },
    { name: 'Delium', modern: 'Delium', lat: 38.4167, lng: 23.6667, type: 'Sanctuary' },
    { name: 'Orchomenus', modern: 'Orchomenus', lat: 38.4928, lng: 22.9756, type: 'Polis' },
    { name: 'Coronea', modern: 'Coronea', lat: 38.4000, lng: 23.0167, type: 'Polis' },
    { name: 'Thespiae', modern: 'Thespiae', lat: 38.3167, lng: 23.1167, type: 'Polis' },
    { name: 'Aulis', modern: 'Aulis', lat: 38.4167, lng: 23.6000, type: 'Port' },

    // Peloponnese - additional sites
    { name: 'Sphacteria', modern: 'Sphacteria', lat: 36.9167, lng: 21.6667, type: 'Island' },
    { name: 'Cythera', modern: 'Kythera', lat: 36.2542, lng: 22.9933, type: 'Island' },
    { name: 'Epidaurus Limera', modern: 'Epidaurus Limera', lat: 36.7167, lng: 23.0833, type: 'Settlement' },
    { name: 'Prasiae', modern: 'Prasiae', lat: 37.0667, lng: 22.9667, type: 'Settlement' },
    { name: 'Hysiae', modern: 'Hysiae', lat: 37.6333, lng: 22.6167, type: 'Settlement' },

    // Chalcidice and Thrace
    { name: 'Torone', modern: 'Torone', lat: 40.0167, lng: 23.8333, type: 'Polis' },
    { name: 'Mende', modern: 'Mende', lat: 40.1333, lng: 23.4833, type: 'Polis' },
    { name: 'Scione', modern: 'Scione', lat: 40.1167, lng: 23.3833, type: 'Polis' },
    { name: 'Aphytis', modern: 'Aphytis', lat: 40.1167, lng: 23.3833, type: 'Settlement' },
    { name: 'Acanthus', modern: 'Acanthus', lat: 40.4500, lng: 23.9167, type: 'Polis' },
    { name: 'Stagira', modern: 'Stagira', lat: 40.5333, lng: 23.7833, type: 'Polis' },
    { name: 'Argilos', modern: 'Argilos', lat: 40.8667, lng: 23.8667, type: 'Polis' },
    { name: 'Eion', modern: 'Eion', lat: 40.8500, lng: 23.9000, type: 'Port' },
    { name: 'Galepsos', modern: 'Galepsos', lat: 40.9167, lng: 24.5667, type: 'Settlement' },
    { name: 'Oisyme', modern: 'Oisyme', lat: 40.9500, lng: 24.6000, type: 'Settlement' },

    // Macedonia
    { name: 'Methone', modern: 'Methone (Macedonia)', lat: 40.3667, lng: 22.6000, type: 'Polis' },
    { name: 'Pydna', modern: 'Pydna', lat: 40.3667, lng: 22.6000, type: 'Polis' },
    { name: 'Therme', modern: 'Therme', lat: 40.5500, lng: 22.9667, type: 'Settlement' },
    { name: 'Beroea', modern: 'Veria', lat: 40.5242, lng: 22.2017, type: 'Polis' },

    // Hellespont and Propontis
    { name: 'Sestos', modern: 'Sestos', lat: 40.2333, lng: 26.4167, type: 'Polis' },
    { name: 'Abydus', modern: 'Abydos', lat: 40.1833, lng: 26.3833, type: 'Polis' },
    { name: 'Lampsacus', modern: 'Lampsacus', lat: 40.3500, lng: 26.6833, type: 'Polis' },
    { name: 'Elaeus', modern: 'Elaeus', lat: 40.0333, lng: 26.1833, type: 'Settlement' },
    { name: 'Cyzicus', modern: 'Cyzicus', lat: 40.3833, lng: 27.8833, type: 'Polis' },
    { name: 'Perinthus', modern: 'Perinthus', lat: 40.9667, lng: 27.9667, type: 'Polis' },
    { name: 'Selymbria', modern: 'Selymbria', lat: 40.9833, lng: 28.1833, type: 'Polis' },
    { name: 'Chalcedon', modern: 'Chalcedon', lat: 40.9875, lng: 29.0306, type: 'Polis' },

    // Sicily - Athenian Expedition sites
    { name: 'Catana', modern: 'Catania', lat: 37.5022, lng: 15.0873, type: 'Polis' },
    { name: 'Naxos', modern: 'Naxos (Sicily)', lat: 37.8256, lng: 15.2656, type: 'Polis' },
    { name: 'Messana', modern: 'Messina', lat: 38.1938, lng: 15.5540, type: 'Polis' },
    { name: 'Camarina', modern: 'Camarina', lat: 36.8667, lng: 14.4500, type: 'Polis' },
    { name: 'Segesta', modern: 'Segesta', lat: 37.9419, lng: 12.8356, type: 'Settlement' },
    { name: 'Leontini', modern: 'Lentini', lat: 37.2833, lng: 14.9500, type: 'Polis' },
    { name: 'Megara Hyblaea', modern: 'Megara Hyblaea', lat: 37.2042, lng: 15.1817, type: 'Polis' },

    // Southern Italy
    { name: 'Thurii', modern: 'Thurii', lat: 39.7333, lng: 16.5000, type: 'Polis' },
    { name: 'Heraclea', modern: 'Heraclea', lat: 40.3833, lng: 16.4333, type: 'Polis' },
    { name: 'Metapontum', modern: 'Metapontum', lat: 40.3833, lng: 16.8333, type: 'Polis' },

    // Islands
    { name: 'Melos', modern: 'Milos', lat: 36.7216, lng: 24.4256, type: 'Polis' },
    { name: 'Andros', modern: 'Andros', lat: 37.8333, lng: 24.9333, type: 'Polis' },
    { name: 'Ceos', modern: 'Kea', lat: 37.6288, lng: 24.3389, type: 'Polis' },
    { name: 'Cythnos', modern: 'Kythnos', lat: 37.3950, lng: 24.4242, type: 'Polis' },
    { name: 'Tenos', modern: 'Tinos', lat: 37.5431, lng: 25.1625, type: 'Polis' },
    { name: 'Scyros', modern: 'Skyros', lat: 38.9000, lng: 24.5500, type: 'Polis' },

    // Central Greece
    { name: 'Heraclea Trachinia', modern: 'Heraclea Trachinia', lat: 38.8167, lng: 22.2167, type: 'Polis' },
    { name: 'Trachis', modern: 'Trachis', lat: 38.8167, lng: 22.2167, type: 'Settlement' },
    { name: 'Daulis', modern: 'Daulis', lat: 38.4667, lng: 22.6000, type: 'Settlement' },
    { name: 'Phocis', modern: 'Phocis', lat: 38.5333, lng: 22.5000, type: 'Region' }
];
