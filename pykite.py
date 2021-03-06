from ctypes import *
import numpy as np

coefficients=np.array([
    [-0.15, 0.005],
    [-0.05, 0.005],
    [0.05, 0.001],
    [0.2, 0.005],
    [0.35, 0.01],
    [0.45, 0.02],
    [0.55, 0.03],
    [0.65, 0.05],
    [0.75, 0.07],
    [0.82, 0.09],
    [0.9, 0.1],
    [1.0, 0.13],
    [1.08, 0.18],
    [1.1, 0.18],
    [1.05, 0.21]
])
bank_angles=np.array([-3, -2, -1, 0, 1, 2, 3])
n_beta=1
'''
class Wind3d(Structure):
    _fields_ = [
        ('m_vel', POINTER(c_double)),
    ]
    def __init__(self):
        pass

class Wind3d_lin(Wind3d):
    _fields_ = [
        ('vel_ground', c_double),
        ('ang_coef', c_double)
    ]
    def _init_(self):
        pass
'''
class vect(Structure):
    _fields_ = [
        ('theta', c_double),
        ('phi', c_double),
        ('r', c_double),
    ]
    def __init__(self, t, p, r):
        self.theta=t
        self.phi=p
        self.r=r

class kite(Structure):
    _fields_ = [
        ('position', vect),
        ('velocity', vect),
        ('wind', c_void_p),
        ('C_l', c_double),
        ('C_d', c_double),
        ('psi', c_double)
    ]
    def __init__(self, initial_pos, initial_vel):
        self.position=initial_pos
        self.velocity=initial_vel
        self.C_l=0.35
        self.C_d=0.01
        self.psi=0
        libkite.init_turboframe_wind(pointer(self))
        #libkite.init_lin_wind(pointer(self), 8, 0.125)
    def __str__(self):
        return "Position: "+str(self.position.theta)+","+str(self.position.phi)+","+str(self.position.r)+", Velocity"+ str(self.velocity.theta)+","+str(self.velocity.phi)+","+str(self.velocity.r)
    def simulate(self, step):
        return libkite.simulation_step(pointer(self), step)
    def evolve_system(self, attack_angle, bank_angle, integration_steps, step):
        self.C_l, self.C_d = coefficients[attack_angle,0], coefficients[attack_angle,1]
        self.psi = np.deg2rad(bank_angles[bank_angle])
        return libkite.simulate(pointer(self), integration_steps, step)
    def beta(self):
        b=np.digitize(libkite.getbeta(pointer(self)), np.linspace(-np.pi/2, np.pi/2, n_beta))
        return 0
    def accelerations(self):
        a=libkite.getaccelerations(pointer(self))
        return a.theta, a.phi, a.r
    def reward(self, learning_step):
        return libkite.getreward(pointer(self))*learning_step
    def wind_gradient(self, value):
        height=self.position.r*np.cos(self.position.theta)
        return vect(value*height,0,0)


def setup_lib(lib_path):
    lib = cdll.LoadLibrary(lib_path)
    lib.simulation_step.argtypes = [POINTER(kite), c_double]
    lib.simulation_step.restype = c_int
    lib.simulate.argtypes =[POINTER(kite), c_int, c_double]
    lib.simulate.restype=c_int
    lib.init_lin_wind.argtypes=[POINTER(kite), c_double, c_double]
    lib.getbeta.argtypes = [POINTER(kite)]
    lib.getbeta.restype=c_double
    lib.getaccelerations.argtypes = [POINTER(kite)]
    lib.getaccelerations.restype=vect
    lib.getreward.argtypes = [POINTER(kite)]
    lib.getreward.restype=c_double
    return lib

libkite=setup_lib("libkite.so")
