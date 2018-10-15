import sys

import pprint; pp = pprint.PrettyPrinter(depth=6)

from neuromllite.sweep.ParameterSweep import ParameterSweep
from neuromllite.sweep.ParameterSweep import NeuroMLliteRunner
       
sys.path.append("..") 
from GenerateHippocampalNet_oc import helper_getcolor

colors = helper_getcolor(None)

if __name__ == '__main__':


    if '-all' in sys.argv:
        
        print('Generating all plots')
        save_fig_dir = './'
        html = '<table>\n'
        
        fixed = {'dt':0.001, 'duration':700}


        vary = {'stim_amp':['%spA'%(i) for i in xrange(-100,500,2)]}
        #vary = {'stim_amp':['%spA'%(i/10.0) for i in xrange(-10,20,5)]}
        #vary = {'stim_amp':['-100pA','0pA','100pA','200pA','300pA','400pA']}
        
        cells = colors.keys()
        #cells = ['olm','ivy']

        for type in cells:
            if type!='ec' and type !='ca3':

                run = True
                #run = False
                
                if run:
                
                    nmllr = NeuroMLliteRunner('Sim_IClamp_%s.json'%type,
                                              simulator='jNeuroML_NEURON')
                    ps = ParameterSweep(nmllr, 
                                        vary, 
                                        fixed,
                                        num_parallel_runs=16,
                                        save_plot_all_to='firing_rates_%s.png'%type,
                                        heatmap_all=True,
                                        save_heatmap_to='heatmap_%s.png'%type,
                                        heatmap_lims=[-100,20],
                                        plot_all=True, 
                                        show_plot_already=False)

                    report = ps.run()

                    #ps.plotLines('stim_amp','average_last_1percent',save_figure_to='average_last_1percent_%s.png'%type)
                    ps.plotLines('stim_amp','mean_spike_frequency',save_figure_to='mean_spike_frequency_%s.png'%type)
                
                height = '160'
                html+='<tr>\n'
                html+='  <td width=30><b>'+type+'</b></td>\n'
                html+='  <td><a href="mean_spike_frequency_%s.png'%type+'">\n'
                html+='    <img alt="?" src="mean_spike_frequency_%s.png'%type+'" height="'+height+'"/></a>\n'
                html+='  </td>\n'
                html+='  <td><a href="firing_rates_%s.png'%type+'">\n'
                html+='    <img alt="?" src="firing_rates_%s.png'%type+'" height="'+height+'"/></a>\n'
                html+='  </td>\n'
                html+='  <td><a href="heatmap_%s.png'%type+'">\n'
                html+='    <img alt="?" src="heatmap_%s.png'%type+'" height="'+height+'"/></a>\n'
                html+='  </td>\n'
                html+='  <td><a href="dt_traces_%s.png'%type+'">\n'
                html+='    <img alt="?" src="dt_traces_%s.png'%type+'" height="'+height+'"/></a>\n'
                html+='  </td>\n'
                html+='  <td><a href="heatmap_dt_%s.png'%type+'">\n'
                html+='    <img alt="?" src="heatmap_dt_%s.png'%type+'" height="'+height+'"/></a>\n'
                html+='  </td>\n'
                html+='  <td><a href="mean_spike_frequency_dt_%s.png'%type+'">\n'
                html+='    <img alt="?" src="mean_spike_frequency_dt_%s.png'%type+'" height="'+height+'"/></a>\n'
                html+='  </td>\n'
                html+='<tr>\n'

        import matplotlib.pyplot as plt
        if not '-nogui' in sys.argv:
            print("Showing plots")
            plt.show()
            
            
        with open(save_fig_dir+'info.html','w') as f:
            f.write('<html><body>\n%s\n</body></html>'%html)
        with open(save_fig_dir+'README.md','w') as f2:
            f2.write('### CA1 cell summary \n%s'%(html.replace('.html','.md')))
        
    elif '-dt' in sys.argv:
        
        optimal_stim = {'olm':100,'sca':100,'pvbasket':350,'ivy':220,'ngf':220,'bistratified':350,'cck':180,'axoaxonic':220,'poolosyn':280}
        #optimal_stim = {'olm':100,'sca':100}
        #optimal_stim = {'olm':100}
        #optimal_stim = {'pvbasket':350}
        

        vary = {'dt':[0.1,0.05,0.025,0.01,0.005,0.0025,0.001,0.0005,0.00025,0.0001]}
        vary = {'dt':[0.025,0.02,0.015,0.01,0.005,0.0025,0.001,0.0005]}
        vary = {'dt':[0.025,0.02,0.015,0.01,0.005,0.0025]}
        #vary = {'dt':[0.025,0.01,0.005,0.0025,0.001]}
        #vary = {'dt':[0.1,0.05,0.025,0.01,0.005]}
        #vary = {'dt':[0.05,0.025,0.01]}
        vary = {'dt':[0.1,0.05,0.025,0.01,0.005,0.0025,0.001]}
        vary = {'dt':[0.025,0.01,0.005,0.0025,0.001,0.0005,0.00025]}

        for type in optimal_stim:
            if type!='ec' and type !='ca3':

                run = True
                
                if run:
                
                    fixed = {'duration':700, 'stim_amp':'%spA'%optimal_stim[type]}
                    
                    nmllr = NeuroMLliteRunner('Sim_IClamp_%s.json'%type,
                                              simulator='jNeuroML_NEURON')
                    ps = ParameterSweep(nmllr, 
                                        vary, 
                                        fixed,
                                        num_parallel_runs=16,
                                        save_plot_all_to='dt_traces_%s.png'%type,
                                        heatmap_all=True,
                                        save_heatmap_to='heatmap_dt_%s.png'%type,
                                        plot_all=True, 
                                        show_plot_already=False)

                    report = ps.run()

                    #ps.plotLines('stim_amp','average_last_1percent',save_figure_to='average_last_1percent_%s.png'%type)
                    ps.plotLines('dt','mean_spike_frequency',save_figure_to='mean_spike_frequency_dt_%s.png'%type, logx=True)
                
                

        import matplotlib.pyplot as plt
        if not '-nogui' in sys.argv:
            print("Showing plots")
            plt.show()
            
    elif '-pois' in sys.argv:
        
        cells = colors.keys()
        cells = ['olm','ivy']
        #cells = ['olm']
        #cells = ['ivy']
        save_fig_dir = './'
        html = '<table>\n'
 
        vary = {'average_rate':['%sHz'%f for f in xrange(1,500,10)]}
        fixed = {'duration':1000, 'number_per_cell':30}
        
        vary = {'average_rate':['%sHz'%f for f in xrange(1,500,10)],
                'number_per_cell':[1,10,30,50,100,300,500]}
                
        vary = {'average_rate':['%sHz'%f for f in xrange(1,500,100)],
                'number_per_cell':[30,50,100]}
                
        vary = {'average_rate':['%sHz'%f for f in xrange(1,2000,200)],
                'seed':[i for i in range(5)]}
                
        fixed = {'duration':1000, 'dt':0.01, 'number_per_cell':20}

        for type in cells:
            if type!='ec' and type !='ca3':

                run = True
                
                if run:
                    nmllr = NeuroMLliteRunner('Sim_PoissonFiringSynapse_%s.json'%type,
                                              simulator='jNeuroML_NEURON')
                    ps = ParameterSweep(nmllr, 
                                        vary, 
                                        fixed,
                                        num_parallel_runs=16,
                                        save_plot_all_to='pois_traces_%s.png'%type,
                                        heatmap_all=False,
                                        plot_all=True, 
                                        show_plot_already=False)

                    report = ps.run()

                    #ps.plotLines('stim_amp','average_last_1percent',save_figure_to='average_last_1percent_%s.png'%type)
                    ps.plotLines('average_rate',
                                 'mean_spike_frequency',
                                 second_param='seed',
                                 save_figure_to='pois_traces_average_rate_%s.png'%type)
                                 
                                
                height = '160'
                html+='<tr>\n'
                html+='  <td width=30><b>'+type+'</b></td>\n'
                html+='  <td><a href="pois_traces_%s.png'%type+'">\n'
                html+='    <img alt="?" src="pois_traces_%s.png'%type+'" height="'+height+'"/></a>\n'
                html+='  </td>\n'
                html+='  <td><a href="pois_traces_average_rate_%s.png'%type+'">\n'
                html+='    <img alt="?" src="pois_traces_average_rate_%s.png'%type+'" height="'+height+'"/></a>\n'
                html+='  </td>\n'
             
                html+='<tr>\n'
                
                

        import matplotlib.pyplot as plt
        if not '-nogui' in sys.argv:
            print("Showing plots")
            plt.show()
            
        with open(save_fig_dir+'poisson_inputs.html','w') as f:
            f.write('<html><body>\n%s\n</body></html>'%html)
        with open(save_fig_dir+'poisson_inputs.md','w') as f2:
            f2.write('### CA1 cells response to poisson inputs \n%s'%(html.replace('.html','.md')))
            
        
    else:
        
        fixed = {'dt':0.01, 'duration':700}

        quick = False
        #quick=True

        vary = {'stim_amp':['%spA'%(i/10.0) for i in xrange(-10,20,2)]}
        vary = {'dt':[0.1,0.05,0.025,0.01,0.005,0.0025,0.001,0.0005,0.00025,0.0001]}
        vary = {'dt':[0.1,0.05,0.025,0.01,0.005,0.0025,0.001]}
        vary = {'dt':[0.1,0.05,0.025,0.01,0.005]}
        
        #vary = {'number_per_cell':[i for i in xrange(0,250,10)]}
        #vary = {'stim_amp':['1pA','1.5pA','2pA']}
        vary = {'stim_amp':['%spA'%(i) for i in xrange(-100,500,50)]}

        type = 'bistratified'
        #type = 'ivy'
        type = 'ngf'
        type = 'olm'
        #type='poolosyn'
        config = 'IClamp'
        #config = 'PoissonFiringSynapse'

        nmllr = NeuroMLliteRunner('Sim_%s_%s.json'%(config,type),
                                  simulator='jNeuroML_NEURON')

        if quick:
            pass

        ps = ParameterSweep(nmllr, vary, fixed,
                            num_parallel_runs=16,
                                  plot_all=True, 
                                  save_plot_all_to='firing_rates_%s.png'%type,
                                  heatmap_all=True,
                                  save_heatmap_to='heatmap_%s.png'%type,
                                  show_plot_already=False)

        report = ps.run()
        ps.print_report()

        #ps.plotLines('stim_amp','average_last_1percent',save_figure_to='average_last_1percent_%s.png'%type)
        ps.plotLines('stim_amp','mean_spike_frequency',save_figure_to='mean_spike_frequency_%s.png'%type)
        #ps.plotLines('dt','mean_spike_frequency',save_figure_to='mean_spike_frequency_%s.png'%type, logx=True)
        #ps.plotLines('number_per_cell','mean_spike_frequency',save_figure_to='poisson_mean_spike_frequency_%s.png'%type)

        import matplotlib.pyplot as plt
        if not '-nogui' in sys.argv:
            print("Showing plots")
            plt.show()