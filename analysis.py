import numpy as np
from math import acos
from Games import FastDgame, SlowDgame
from geometries import LineTarget

def play_fastD_game(xd0, xi, xd1, ni=1, nd=2):
	game = FastDgame(LineTarget(), None, ni=ni, nd=nd)
	game.reset({'D0': xd0, 'I0': xi, 'D1': xd1})
	ts_play, xs_play = game.advance(5., game.f_strategy, game.f_strategy, close_adjust=False)
	# ts_exp,xs_exp  = game.replay_exp()
	## xs_play = np.concatenate((xds[0], xis[0], xds[1]),-1)
	game.plotter.plot({'play':xs_play}, 'play', fname='play_traj.png')
	game.plotter.animate(ts_play, xs_play, xrs=xs_play)

def generate_data_for_exp(S, T, gmm, D, delta, ni=1, nd=2, param_file='traj_param_100.csv'):
	game = SlowDgame(LineTarget(), None, ni=ni, nd=nd)
	xs_ref = game.generate_analytic_traj(S, T, gmm, D, delta, file=param_file)
	game.reset({'D0': xs_ref['D0'][0,:], 'I0': xs_ref['I0'][0,:], 'D1': xs_ref['D1'][0,:]})
	ts, xs_play = game.advance(5., game.nn_strategy, game.nn_strategy, close_adjust=True)
	game.plotter.plot({'ref':xs_ref, 'play':xs_play}, 'play')

def replay_exp(res_dir='res1/', ni=1, nd=2):
	with open('exp_results/'+res_dir+'/info.csv', 'r') as f:
		data = f.readlines()
		for line in data:
			if 'vd' in line:
				vd = float(line.split(',')[-1])
			if 'vi' in line:
				vi = float(line.split(',')[-1])
	if vd < vi:
		game = SlowDgame(LineTarget(), res_dir=res_dir, ni=ni, nd=nd)
		xs_ref = game.reproduce_analytic_traj()
		ts_ref = None
	else:
		game = FastDgame(LineTarget(), res_dir=res_dir, ni=ni, nd=nd)
		ts_ref, xs_ref = game.advance(6., game.f_strategy, game.f_strategy, close_adjust=False)

	game.reset({role: x[0,:] for role, x in xs_ref.items()})
	ts, xs_exp = game.replay_exp()
	game.plotter.plot({'ref':xs_ref, 'exp':xs_exp}, 'exp', fname='replay_traj.png')
	game.plotter.animate(ts, xs_exp, xrs=xs_ref)


if __name__ == '__main__':

	# generate_data_for_exp(0.3,4,acos(1/1.5)+0.1,0,0.09999999,param_file='traj_param_11.csv')
	play_fastD_game(np.array([-1, 0]), np.array([-0.2, 0.5]), np.array([1, 0]))
	# replay_exp(res_dir='res6/', ni=1, nd=2)