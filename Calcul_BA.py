from prettytable import *
import pandas as pd
from math import *

# _________ Tout les entrer ____________
remarques = '''REMARQUES :
>> Le sens de poutre principale X !
>> Le sens de poutre secondaire Y !
>> Les longures entre axes !
>> Les dimension des pouteau (architecte) (a x b):  a >>> sens X & b >>> sens Y
'''
print(remarques)
def Information():
    """ Entrer les informations necessaire """
    global L_x, L_y, h_rdc, G, Q, a, b, Longures_X, Longures_Y, Longure_axeY, Longure_axeX
    L_x = int(input('Entrer le nombre de travée sens X : '))
    L_y = int(input('Entrer le nombre de travée sens Y : '))
    h_rdc = float(input('Entrer l\'hauteur de la RDC :'))
    G = float(input('Entrer la charges permanent G(KN/m^2) : '))
    Q = float(input('Entrer la charges exploitation Q(KN/m^2) : '))
    a = float(input('Entrer longure a de poteau en (m) : '))
    b = float(input('Entrer largeur b de poteau en (m) : '))
    Longures_X = []
    Longures_Y = []
    Longure_axeX = []
    Longure_axeY = []
    for i in range(L_x):
        Longure_X = float(input('Enter longure {} sens X (m) : '.format(i)))
        Longures_X.append(Longure_X - a )
        Longure_axeX.append(Longure_X)
    for i in range(L_y):
        Longure_Y = float(input('Enter longures {} sens Y (m) : '.format(i)))
        Longures_Y.append(Longure_Y - b)
        Longure_axeY.append(Longure_Y)

# __ Epaiseur de la dalle  ______
def Epaiseur_ht():
    """ Calcul l'épaiseur de la dalle !"""
    global ht
    h_corpcreux = [20, 24, 25, 26, 29, 30, 35]
    ht = max(Longures_Y) * 100 / 22.5
    for i in h_corpcreux:
        if i > ht:
            ht = i
            print('L\'epaisur de la dalle = ', ht)
            break
    return ht


# __ prédimensionnement des poutres principal et secondure _____
def PP_PS():
    """Prédimensionnement des poutres principal et secondure"""
    global h_PP, b_PP, h_PS, b_PS
    L_maxX = max(Longures_X)*100
    h_PP = int(input('choix hauteur de poutre principale {} < h < {} (cm): '.format(L_maxX / 15, L_maxX / 10)))
    b_PP = int(input('choix largeur de poutre principale {} < b < {} (cm): '.format(0.3 * h_PP, 0.7 * h_PP)))
    print('le dimension de poutre principale ({}x{})'.format(b_PP, h_PP))
    L_maxY = max(Longures_Y)*100
    h_PS = int(input('choix hauteur de poutre secondure {} < h < {} (cm): '.format(L_maxY / 15, L_maxY / 10)))
    b_PS = int(input('choix largeur de poutre secondure {} < b < {} (cm): '.format(0.3 * h_PS, 0.7 * h_PS)))
    print('le dimension de poutre secondure ({}x{})'.format(b_PS, h_PS))
    # return h_PP, b_PP, h_PS, b_PS

# __ prédimensionnement des poteaux ______
def Poteaux(h_rdc):
    """Prédimensionnement des poteaux"""
    global a_poteau
    Sf = float(input('Enter la surface afirent Sf en (m^2): '))
    Poid_PP = float(input('Enter la poid su poutre principale (KN): '))
    Poid_PS = float(input('Enter la poid su poutre secondaire (KN): '))
    Poid_p = G * Sf
    G_Poteaux = Poid_p + Poid_PP + Poid_PS
    Q_Poteaux = Q * Sf
    Nu_Poteaux = 1.35 * G_Poteaux + 1.5 * Q_Poteaux
    a_poteau = (sqrt(0.064 * Nu_Poteaux * 10 ** -3) + 0.02) * 10 ** 2
    if a_poteau < 25:
        a_poteau = 25
    else:
        for i in range(0, 100, 5):
            if i > a_poteau:
                a_poteau = i
                break
    print('Les dimensions des poteaux ({}x{})'.format(a_poteau, a_poteau))
    """ verification des poteaux au flambement """
    verification = False
    while verification:
        Lf = 0.7 * h_rdc
        Lambda = sqrt(12) * Lf / a_poteau
        if Lambda < 35:
            print('c\'est condtions de flambment verifiée !')
            verification = True
        else:
            print('c\'est condtions de flambment non verifiée !')
            a_poteau = int(input('Entrer novelle dimension de poteau :'))
            verification = False
    return a_poteau


class Forfaitaire():
    def __init__(self, L_y, G, Q, Longures_Y, Longure_axeY, a_poteau):
        self.G = G
        self.Q = Q
        self.Travee = L_y
        self.Longures_Y = Longures_Y
        self.Longure_axeY = Longure_axeY
        self.a_poteau = a_poteau
        self.M_0 = []
        self.M_aw = []
        self.M_ae = []
        self.M_t = []
        self.T_w = []
        self.T_e = []
        self.qu = 1.35 * self.G * 0.6 + 1.5 * self.Q * 0.6
        self.qser = self.G * 0.6 + self.Q * 0.6
        self.Calcul()

    def Moments_iso(self):  # _______Moments Isostatiques_____
        for i in range(self.Travee):
            Mo_0 = (self.qu * self.Longures_Y[i] ** 2) / 8
            self.M_0.append(Mo_0)

    def Moments_app(self):  # _______Moments En Appuis _______
        for i in range(self.Travee):
            if self.Travee == 2:
                if i == 0:
                    moment_app = 0.2 * self.M_0[i]
                    self.M_aw.append(moment_app)
                else:
                    moment_app = 0.6 * max(self.M_0)
                    self.M_ae.append(moment_app)
                    self.M_aw.append(moment_app)
                    if i == self.Travee - 1:
                        moment_app = 0.2 * self.M_0[i]
                        self.M_ae.append(moment_app)
            else:
                if i == 0:
                    moment_app = 0.2 * self.M_0[i]
                    self.M_aw.append(moment_app)
                else:
                    moment_app = 0.5 * max(self.M_0[i - 1], self.M_0[i])
                    self.M_ae.append(moment_app)
                    self.M_aw.append(moment_app)
                    if i == self.Travee - 1:
                        moment_app = 0.2 * self.M_0[i]
                        self.M_ae.append(moment_app)

    def Moments_tr(self):  # _______Moments En Travée _______
        for i in range(self.Travee):
            alpha = 0.3 * self.Q / (self.Q + self.G)
            moment_tra = max((1 + alpha) * self.M_0[i], 1.05 * self.M_0[i]) - (self.M_aw[i] + self.M_ae[i]) / 2
            if i == 0 or i == self.Travee - 1:
                moment_ver = (1.2 + alpha) * self.M_0[i] / 2
            else:
                moment_ver = (1 + alpha) * self.M_0[i] / 2
            Moment_tra = max(moment_tra, moment_ver)
            self.M_t.append(Moment_tra)

    def Efforts_tran(self):  # _______ L'éffort Tranchant ______
        for i in range(self.Travee):
            Tw = self.qu * self.Longures_Y[i] / 2 + (self.M_aw[i] - self.M_ae[i]) / self.Longures_Y[i]
            self.T_w.append(Tw)
            Te = - self.qu * self.Longures_Y[i] / 2 + (self.M_aw[i] - self.M_ae[i]) / self.Longures_Y[i]
            self.T_e.append(Te)

    def Dessin_table(self):  # _______ Affichage _________________
        Data = {'L ': self.Longures_Y, 'M˳': self.M_0, 'Mw': self.M_aw, 'Me': self.M_ae, 'Mt': self.M_t, 'Tw': self.T_w,
                'Te': self.T_e}
        table = PrettyTable(['L', 'M˳', 'Mw', 'Me', 'Mt', 'Tw', 'Te'])
        for i in range(self.Travee):
            table.add_row(
                [self.Longure_axeY[i], format(self.M_0[i], '.3f'), format(self.M_aw[i], '.3f'), format(self.M_ae[i], '.3f'),
                 format(self.M_t[i], '.3f'), format(self.T_w[i], '.3f'), format(self.T_e[i], '.3f')])
        print(table)
        df = pd.DataFrame(Data)
        print(df)

    def Calcul(self):
        self.Moments_iso()
        self.Moments_app()
        self.Moments_tr()
        self.Efforts_tran()
        self.Dessin_table()


if __name__ == '__main__':
    Information()
    Epaiseur_ht()
    PP_PS()
    Poteaux(h_rdc)
    easy = Forfaitaire(L_y, G, Q, Longures_Y, Longure_axeY, a_poteau)
    # easy.Calcul()
