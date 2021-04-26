#!/usr/bin/python3

import json

agrupaciones = {
    '01': 'AP', # 'ACCION POPULAR',
    '02': 'APP', # 'ALIANZA PARA EL PROGRESO',
    '03': 'AVANZA', # 'AVANZA PAIS - PARTIDO DE INTEGRACION SOCIAL',
    '04': 'DD', # 'DEMOCRACIA DIRECTA',
    '05': 'FAJVL', # 'EL FRENTE AMPLIO POR JUSTICIA, VIDA Y LIBERTAD',
    '06': 'FREPAP', # 'FRENTE POPULAR AGRICOLA FIA DEL PERU - FREPAP',
    '07': 'FP', # 'FUERZA POPULAR',
    '08': 'JPP', # 'JUNTOS POR EL PERU',
    '10': 'SP', # 'PARTIDO DEMOCRATICO SOMOS PERU',
    '11': 'PM', # 'PARTIDO MORADO',
    '12': 'PNP', # 'PARTIDO NACIONALISTA PERUANO',
    '13': 'CONTIGO', # 'PARTIDO POLITICO CONTIGO',
    '14': 'PL', # 'PARTIDO POLITICO NACIONAL PERU LIBRE',
    '15': 'PPC', # 'PARTIDO POPULAR CRISTIANO - PPC',
    '17': 'PPS', # 'PERU PATRIA SEGURA',
    '18': 'PODEM', # 'PODEMOS PERU',
    '19': 'RUNA', # 'RENACIMIENTO UNIDO NACIONAL',
    '20': 'RP', # 'RENOVACION POPULAR',
    '21': 'UPP', # 'UNION POR EL PERU',
    '22': 'VN', # 'VICTORIA NACIONAL',

    '79': 'VALIDOS',    # Addition
    '80': 'BLANCOS',
    '81': 'NULOS',
    '82': 'EMITIDOS',   # Addition
    '83': 'HABILES'     # Addition
}

ubigeos = {
    'D44001': 'AMAZONAS',
    'D44002': 'ANCASH',
    'D44003': 'APURIMAC',
    'D44004': 'AREQUIPA',
    'D44005': 'AYACUCHO',
    'D44006': 'CAJAMARCA',
    'D44007': 'CALLAO',
    'D44008': 'CUSCO',
    'D44009': 'HUANCAVELICA',
    'D44010': 'HUANUCO',
    'D44011': 'ICA',
    'D44012': 'JUNIN',
    'D44013': 'LA LIBERTAD',
    'D44014': 'LAMBAYEQUE',
    'D44015': 'LIMA',
    'D44016': 'LIMA PROVINCIAS',
    'D44017': 'LORETO',
    'D44018': 'MADRE DE DIOS',
    'D44019': 'MOQUEGUA',
    'D44020': 'PASCO',
    'D44021': 'PIURA',
    'D44022': 'PUNO',
    'D44023': 'SAN MARTIN',
    'D44024': 'TACNA',
    'D44025': 'TUMBES',
    'D44026': 'UCAYALI',
    'D44027': 'EXTRANJERO'    # Residentes en el extranjero, oficialmente
}
escanos = {
    'D44001':  2, # 'AMAZONAS',
    'D44002':  5, # 'ANCASH',
    'D44003':  2, # 'APURIMAC',
    'D44004':  6, # 'AREQUIPA',
    'D44005':  3, # 'AYACUCHO',
    'D44006':  6, # 'CAJAMARCA',
    'D44007':  4, # 'CALLAO',
    'D44008':  5, # 'CUSCO',
    'D44009':  2, # 'HUANCAVELICA',
    'D44010':  3, # 'HUANUCO',
    'D44011':  4, # 'ICA',
    'D44012':  5, # 'JUNIN',
    'D44013':  7, # 'LA LIBERTAD',
    'D44014':  5, # 'LAMBAYEQUE',
    'D44015': 33, # 'LIMA',
    'D44016':  4, # 'LIMA PROVINCIAS',
    'D44017':  4, # 'LORETO',
    'D44018':  1, # 'MADRE DE DIOS',
    'D44019':  2, # 'MOQUEGUA',
    'D44020':  2, # 'PASCO',
    'D44021':  7, # 'PIURA',
    'D44022':  5, # 'PUNO',
    'D44023':  4, # 'SAN MARTIN',
    'D44024':  2, # 'TACNA',
    'D44025':  2, # 'TUMBES',
    'D44026':  3, # 'UCAYALI',
    'D44027':  2, # 'EXTRANJERO'    # Residentes en el extranjero, oficialmente
}

ubivec = list(ubigeos.values())

def jget(n):
    with open(f"cong-{'%02d'%n}.json") as f: return json.load(f)

fix = lambda s:int(s.replace(',', ''))

def votes(dist):
    summ = dist['summary']
    votos = { codigo[-2:] : fix(voto)
                for codigo, voto in (
                    (part['C_CODI_AGRUPOL'], part['TOTAL_VOTOS'])
                     for part in dist['results'])
                if codigo is not None
        }
    votos['79'] = sum(voto for k, voto in votos.items() if k < '70')
    votos['82'] = votos['79'] + votos['80'] + votos['81']
    votos['83'] = fix(summ['ELECTORES_HABIL'])

    return ( summ['CCODI_UBIGEO'], votos )


def read_votes():
    return dict(votes(jget(codi)) for codi in range(1, 28))

def mesas(dist):
    summ = dist['summary']
    cont = fix(summ['CONT_NORMAL'])
    tot = fix(summ['MESAS_HABILES'])
    no_inst = fix(summ['MESAS_NO_INST'])
    anul = fix(summ['CONT_ANULADA'])
    return ( summ['CCODI_UBIGEO'], {
        'cont': cont,
        'tot': tot,
        'no_inst': no_inst,
        'mult': (tot - no_inst) / cont
    })

def read_mesas():
    return dict(mesas(jget(codi)) for codi in range(1, 28))

def sum_votes(data):
    return { k : sum(votos.get(k, 0) for votos in data.values())
             for k in agrupaciones }

def dhondt(votos, ncurul):
    curules = {k: 0 for k in votos}
    for i in range(ncurul):
        _, gana = max((votos[k] / (alloc + 1), k)
                   for k, alloc in curules.items())
        curules[gana] += 1
    return {k:a for k, a in curules.items() if a > 0}

def dhondtq(votos, ncurul):
    curules = {k: 0 for k in votos}
    for i in range(ncurul):
        _, gana = max((votos[k] / (alloc + 1), k)
                   for k, alloc in curules.items())
        curules[gana] += 1
        q = votos[gana] / curules[gana]
    return {k : v / q for k, v in votos.items()}

def report_voto(total):
    col1 = 1 + max(len(v)+len(str(total[k]))
                   for k, v in agrupaciones.items() if k < '70')
    lines = [
          f"{agrupaciones[k]:{col1-len(str(v))}}{v} {v/total['79']*100:5.2f}%"
          for v, k in sorted(((v, k) for k, v in total.items() if k < '70'),
                             reverse = True)
        ]
    rows = (len(lines) + 2) // 3
    print('\n'.join('      '.join(lines[i] for i in range(row, len(lines), rows))
                    for row in range(rows)))

from itertools import zip_longest
def report_represent(total, passed):
    rep = sum(total[k] for k in passed)
    val, bla, nul, vot, hab = [ total[str(k)] for k in range(79, 84) ] 
    pct = lambda n, d: "{:5.2f}%".format(100*n/d)
    matrix = [
      ["", "",         "%",        "%",       "%"],
      ["", "", "Electores",    "Votos",   "Votos"],
      ["", "",   "Hábiles", "Emitidos", "Válidos"],
      ["Electores hábiles",   hab],
      ["Votos emitidos",      vot, pct(vot, hab)],
      ["Votos nulos",         nul, pct(nul, hab), pct(nul, vot)],
      ["Votos blancos",       bla, pct(bla, hab), pct(bla, vot)],
      ["Votos válidos",       val, pct(val, hab), pct(val, vot)],
      ["Votos representados", rep, pct(rep, hab), pct(rep, vot), pct(rep, val)]
    ]
    lens = list(map(max, zip_longest(*([ len(str(s)) for s in row ]
                                       for row in matrix),
                                     fillvalue = 0)))
    for row in matrix: row[0] = row[0].ljust(lens[0])
    print('\n'.join('   '.join(str(s).rjust(lens[k])
                                  for k, s in enumerate(row))
                    for row in matrix))

def report_curul(congreso, passed):
    col1_len = max(len(ubigeos[codigo]) for codigo in congreso)
    print(' '*(col1_len+1)
          + ' '.join(agrupaciones[k][:5].center(5) for k in passed)
          + ' TOTAL')
    print('\n'.join(ubigeos[codigo].ljust(col1_len)
                    + ' '.join(str(curul.get(k, '--')).rjust(5)
                              for k in passed)
                    + ' ' + str(sum(curul.get(k, 0) for k in passed)).rjust(5)
                    for codigo, curul in congreso.items()))
    print('TOTAL'.ljust(col1_len)
          + ' '.join(str(sum(curul.get(k, 0)
                         for curul in congreso.values()))
                     .rjust(5)
                     for k in passed)
          + ' ' + str(sum(curul.get(k, 0)
                          for k in passed for curul in congreso.values()))
                  .rjust(5))

from math import trunc
def report_cifra(congreso, passed):
    col1_len = max(len(ubigeos[codigo]) for codigo in congreso)
    print(' '*(col1_len+1)
          + ' '.join(agrupaciones[k][:5].center(5) for k in passed)
          + ' TOTAL')
    print('\n'.join(ubigeos[codigo].ljust(col1_len + 1)
                    + ' '.join('{:5.3f}'.format(curul.get(k,0)) for k in passed)
                    + ' ' + str(sum(trunc(v) for v in curul.values())).rjust(4)
                    for codigo, curul in congreso.items()))
    print('TOTAL'.ljust(col1_len)
          + ' '.join(str(sum(trunc(curul.get(k, 0))
                             for curul in congreso.values()))
                     .rjust(5)
                     for k in passed)
          + ' ' + str(sum(trunc(curul.get(k, 0))
                          for k in passed for curul in congreso.values()))
                  .rjust(5))

def report_by_dist(congreso):
    for codigo, curules in congreso.items():
        print(ubigeos[codigo] + ': ')
        print('\n'.join(f"  {agrupaciones[k]:8} {alloc:2}"
                        for k, alloc in curules.items()))

def report_by_part(congreso, keys):
    tot = {}
    for k in keys:
        print(agrupaciones[k] + ': ')
        for codigo, curules in congreso.items():
            if k in curules:
                tot[k] = tot.get(k,0) + curules[k]
                print(f"  {curules[k]:2} {ubigeos[codigo]}")
    print("Congreso:")
    print('\n'.join(f"  {bancada:2} {agrupaciones[codigo]}"
                    for codigo, bancada in tot.items()))

valla = lambda total, barra: sorted((k for k, tot in total.items()
                                     if k < '70' and tot >= barra * total['79']),
                                    key = lambda k: total[k],
                                    reverse = True)

restrict = lambda dct, keys: { k: dct[k] for k in keys if k in dct }

data = read_votes()
total = sum_votes(data)
passed = valla(total, 0.05)
def adjust(votos, mesas):
    mult = mesas['mult']
    return { part : round(voto * mult) for part, voto in votos.items() }
mesa_data = read_mesas()
adj_data = { dist : adjust(votos, mesa_data[dist])
             for dist, votos in data.items() }
adj_total = sum_votes(adj_data)

congreso = {
    codigo : dhondt(restrict(votos, passed), escanos[codigo])
        for codigo, votos in data.items() }
# adj_congreso = {
#     codigo : dhondt(restrict(votos, passed), escanos[codigo])
#          for codigo, votos in adj_data.items() }
cifras = {
    codigo : dhondtq(restrict(votos, passed), escanos[codigo])
         for codigo, votos in data.items() }
# adj_cifras = {
#     codigo : dhondtq(restrict(votos, passed), escanos[codigo])
#          for codigo, votos in adj_data.items() }
w = 81
hdr = lambda s: print('\n'.join(("", "-"*w, s.center(w), '-'*w)))
hdr("Voto por partido")
report_voto(total)
hdr("Voto por partido adjustado (est.)")
report_voto(adj_total)
hdr("Representatividad del voto")
report_represent(total, passed)
# hdr("Congresistas por partido por distrito (adj., est.)")
# report_curul(adj_congreso, passed)
# hdr("Voto por cifra repartidor (adj., est.)")
# report_cifra(adj_cifras, passed)
hdr("Congresistas por partido por distrito (est.)")
report_curul(congreso, passed)
hdr("Voto por cifra repartidor")
report_cifra(cifras, passed)
# report_by_dist(congreso)
# report_by_part(congreso, passed)
