from django.contrib.auth.models import User

users = [
    'amk283',
    'ant43',
    'axz242',
    'bab179',
    #'bms146',
    'bsk61',
    'bgs27',
    #'cjn39',
    'dgk37',
    'dcl79',
    'ebk30',
    'eph34',
    'dew124',
    'gfc21',
    'jrz14',
    'jpc106',
    #'jwc160',
    #'jdw144',
    'jdz17',
    #'jmc329',
    'jah301',
    'jrb291',
    'jcp103',
    'jms580',
    'wjb48',
    'mjy41',
    'mdd91',
    'nlb55',
    'mjp184',
    'rsm131',
    'sie3',
    'sjt62',
    'stl40',
    #'srn24',
    'sxp964',
    'tpf15',
    'cwc59',
    'wct15'
]

for u in users:
    newuser = User()
    newuser.username = u
    newuser.save()

