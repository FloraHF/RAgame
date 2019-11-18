import matplotlib.pyplot as plt
import numpy as np
from math import pi, sin, cos

from geometries import dominant_region
from strategies_fastD import depth_in_target

class Plotter(object):
	"""docstring for Plotter"""
	def __init__(self, target, a, r):

		self.fig, self.ax = plt.subplots()
		self.linestyles = {'play': (0, ()), 'ref':(0, (6, 3)), 'exp':(0, (3, 1))}
		self.colors = {'D0': 'g', 'I0': 'r', 'D1': 'b'}
		self.target_specs = {'line':(0, ()), 'color':'k'}
		self.dcontour_specs = {'line':(0, ()), 'color':'k'}
		self.xlim = [-r, r]
		self.ylim = [-r, r]

		self.r = r
		self.a = a
		self.target = target

	def get_data(self, fn, midx=0, midy=0, kx=1., ky=1., n=50, arg=None):
		x = np.linspace(midx+kx*self.xlim[0], midx+kx*self.xlim[1], n)
		y = np.linspace(midy+ky*self.ylim[0], midy+ky*self.ylim[1], n)
		X, Y = np.meshgrid(x, y)
		D = np.zeros(np.shape(X))
		for i, (xx, yy) in enumerate(zip(X, Y)):
			for j, (xxx, yyy) in enumerate(zip(xx, yy)):
				if arg is not None:
					D[i,j] = fn(np.array([xxx, yyy]), arg)
				else:
					D[i,j] = fn(np.array([xxx, yyy]))
		return {'X': X, 'Y': Y, 'data': D}

	def plot_target(self, n=50):
		if self.target.__name__ == 'line':
			kx, ky = 2.5, 1.
		else:
			kx, ky = 3., 3.
		tgt = self.get_data(self.target, kx=kx, ky=ky)
		CT = self.ax.contour(tgt['X'], tgt['Y'], tgt['data'], [0], linestyles=(self.target_specs['line'],))
		plt.contour(CT, levels = [0], colors=(self.target_specs['color'],), linestyles=(self.target_specs['line'],))

	def plot_dr(self, xi, xds, ind=True):
		k = 4.

		nd = len(xds)
		def get_dr(x):
			return dominant_region(x, xi, xds, self.a)
		def get_dr_ind(x, xd):
			return dominant_region(x, xi, [xd], self.a)
		# dr individual
		if ind and nd > 1:
			for p, c in self.colors.items():
				if 'D' in p:
					i = int(p[-1])
					if i < nd:
						xd = xds[i]
						# print(i, xd)
						dr = self.get_data(get_dr_ind, kx=k, ky=k, arg=xd)
						CD = self.ax.contour(dr['X'], dr['Y'], dr['data'], [0], linestyles='dashed')
						plt.contour(CD, levels = [0], colors=(self.colors[p],), linestyles=('dashed',))
	    # dr unioned
		dr = self.get_data(get_dr, midx=xi[0], midy=xi[1], kx=k, ky=k)
		CD = self.ax.contour(dr['X'], dr['Y'], dr['data'], [0], linestyles='solid')
		plt.contour(CD, levels = [0], colors=(self.colors['I0'],), linestyles=('solid',))
		# locations of players
		self.ax.plot(xi[0], xi[1], '.', color=self.colors['I0'])
		for p, c in self.colors.items():
			if 'D' in p:
				i = int(p[-1])
				if i < nd:
					self.ax.plot(xds[i][0], xds[i][1], '.', color=self.colors[p])

	def plot_dcontour(self, xi, xds, levels=[-2., 0., 2.]):
		def get_constd(x):
			solx = depth_in_target(x, xds, self.target, self.a)
			return self.target(solx)

		vctr = self.get_data(get_constd, midx=xi[0], midy=xi[1], kx=5., ky=5.)
		CC = self.ax.contour(vctr['X'], vctr['Y'], vctr['data'], [0], linestyles=(self.dcontour_specs['line'],))
		self.ax.clabel(CC, inline=True, fontsize=10)
		self.ax.contour(vctr['X'], vctr['Y'], vctr['data'], levels=levels, colors=(self.dcontour_specs['color'],), linestyles=(self.dcontour_specs['line'],))
	
	def plot_capture_ring(self, player, situation, x, n=50):
		xs, ys = [], []
		for t in np.linspace(0, 2*pi, n):
			xs.append(x[0] + self.r*cos(t))
			ys.append(x[1] + self.r*sin(t))
		self.ax.plot(xs, ys, color=self.colors[player], linestyle=self.linestyles[situation])

	def plot_traj(self, player, situation, xs):
		self.ax.plot(xs[:,0], xs[:,1], color=self.colors[player], linestyle=self.linestyles[situation])

	def plot_connect(self, p1, p2, xs1, xs2, skip=20):
		n = xs1.shape[0]
		for i, (x1, x2) in enumerate(zip(xs1, xs2)):
			if i%skip == 0 or i==n-1:
				self.ax.plot([x1[0], x2[0]], [x1[1], x2[1]], 'b--')
				self.ax.plot(x1[0], x1[1], 'o', color=self.colors[p1])
				self.ax.plot(x2[0], x2[1], 'o', color=self.colors[p2])

	def show_plot(self):
		self.ax.axis('equal')
		self.ax.grid()
		plt.show()

	def plot(self, xs):
		self.plot_target()
		for situ, x in xs.items():
			for i, xi in enumerate(x[0]):
				self.plot_traj('I'+str(i), situ, xi)
			for d, xd in enumerate(x[1]):
				p = 'D'+str(d)
				self.plot_traj(p, situ, xd)
				self.plot_capture_ring(p, situ, xd[-1, :])
			if situ == 'play':
				self.plot_connect('I0', 'D0', x[0][0], x[1][0])
				self.plot_connect('I0', 'D1', x[0][0], x[1][1])

		# xi0 = xs['play'][0][0][0, :]
		# xd0s = [xd[0, :] for xd in xs['play'][1]]
		# self.plot_dr(xi0, xd0s, ind=True)
		# self.plot_dcontour(xi0, xd0s)

		self.show_plot()

	def reset(self):
		self.ax.clear()