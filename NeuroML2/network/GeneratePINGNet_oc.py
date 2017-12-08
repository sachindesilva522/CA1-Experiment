#!/usr/bin/python
# -*- coding: utf-8 -*-
""" 
Creates a PC-BC network, producing gamma oscillation - generated by PING mechanism
The script is based on the NeuroML version of the model and aims to show easy reusability!
Authors: András Ecker, Padraig Gleeson, last update: 10.2017
"""

import sys
import warnings
# NeuroML specific libraries
import neuroml
from pyneuroml import pynml
import opencortex.core as oc
import opencortex.build as oc_build
# helper functions from other scripts
from GenerateHippocampalNet_oc import helper_getcolor  # just to be consistent with other scripts


def scale(num, scale, min_=3):
    """helper function to scale network"""
    new_num = int(num * scale)   
    return new_num if new_num >= min_ else min_


def add_pop(nml_doc, network, cell_type, pop_size, duration=None, rate=None):
    """adds population using opencortex function"""
    
    if cell_type not in ["ca3", "ec"]:  # "real" cells have template
        pop = oc.add_population_in_rectangular_region(network,
                                                       pop_id="pop_%s"%cell_type, cell_id="%scell"%cell_type,
                                                       size=pop_size,
                                                       x_min=0, y_min=0, z_min=0,
                                                       x_size=2000, y_size=500, z_size=1000,
                                                       color=helper_getcolor(cell_type))
        
        pop.properties.append(neuroml.Property("radius", 5))                                     
        return pop
                                                   
    else:
        spike_gen = oc.add_spike_source_poisson(nml_doc, id="stim_%s"%cell_type,
                                                start="0ms", duration="%fms"%duration, rate="%fHz"%rate)  # duration and rate used only here
        
        # add outer stimulations outside of the slice... (to get better visualization on OSB)                                       
        if cell_type == "ca3":
            x_min = 0
        elif cell_type == "ec":
            x_min = 1900
        
        return oc.add_population_in_rectangular_region(network,
                                                       pop_id="pop_%s"%cell_type, cell_id=spike_gen.id,
                                                       size=pop_size,
                                                       x_min=x_min, y_min=550, z_min=450,
                                                       x_size=100, y_size=100, z_size=100,
                                                       color=helper_getcolor(cell_type))
                                                 
                                                  
def add_proj(network, prepop, postpop, ncons, post_seg_group, weight_mult=1):
    """adds targeted projection using opencortex function"""
    
    import re
    precell_type = re.split(r'\_', prepop.id)[1]
    postcell_type = re.split(r'\_', postpop.id)[1]
    
    if precell_type not in ["ca3", "ec"]:
        pre_seg_group = "soma_group"
    else:
        pre_seg_group = None  # will leave preSegmentId and preFractionAlong in the generated file (which is the way how 'artificial cells' connect to 'real cells')
    
    return oc.add_targeted_projection(network,
                                      prefix="proj",
                                      presynaptic_population=prepop,
                                      postsynaptic_population=postpop,
                                      targeting_mode="convergent",
                                      synapse_list=["syn_%s_to_%s"%(precell_type, postcell_type)],
                                      number_conns_per_cell=ncons,
                                      pre_segment_group=pre_seg_group,
                                      post_segment_group=post_seg_group,
                                      delays_dict={"syn_%s_to_%s"%(precell_type, postcell_type):3},
                                      weights_dict={"syn_%s_to_%s"%(precell_type, postcell_type):weight_mult})


def generate_PING_net(networkID, dPopsize, dNconns, dWeightMults, rate=5,
                      generate_LEMS=True, duration=100, dt=0.01, format_="xml", target_dir="./",
                      simulation_seed=12345, network_seed=12345):
    """generates PC-BC network using methods above"""
    
    if dt > 0.015:
        warnings.warn("\n***** dt bigger than 0.015 results continuous PV+BC spiking ! *****\n")
        
    relative = "../"
    if "test" in target_dir:
        relative = "../../"
    
    nml_doc, network = oc.generate_network(networkID, network_seed=network_seed, temperature="34degC")
        
    # include necessary files
    if dPopsize["poolosyn"] > 0:
        nml_doc.includes.append(neuroml.IncludeType(href=relative+"cells/poolosyn.cell.nml"))
        # workaround to handle opencortex's way of including cell templates:
        oc_build.cell_ids_vs_nml_docs["poolosyncell"] = pynml.read_neuroml2_file("../cells/poolosyn.cell.nml", include_includes=False) 
    if dPopsize["pvbasket"] > 0:
        nml_doc.includes.append(neuroml.IncludeType(href=relative+"cells/pvbasket.cell.nml"))
        oc_build.cell_ids_vs_nml_docs["pvbasketcell"] = pynml.read_neuroml2_file("../cells/pvbasket.cell.nml", include_includes=False)   
    nml_doc.includes.append(neuroml.IncludeType(href=relative+"synapses/exp2Synapses.synapse.nml"))
    
    # create populations
    dPops = {}
    pop_poolosyn = add_pop(nml_doc, network, "poolosyn", dPopsize["poolosyn"])
    pop_pvbasket = add_pop(nml_doc, network, "pvbasket", dPopsize["pvbasket"])
    dPops["poolosyn"] = pop_poolosyn; dPops["pvbasket"] = pop_pvbasket
    pop_ca3 = add_pop(nml_doc, network, "ca3", dPopsize["stim"], duration=duration, rate=rate)
    pop_ec = add_pop(nml_doc, network, "ec", dPopsize["stim"], duration=duration, rate=rate)
                                                       
    # add connections (synapses as in conndata_430.dat and syndata_120.dat)
    total_cons = 0
    proj_poolosyn_to_pvbasket = add_proj(network,
                                         prepop=dPops["poolosyn"], postpop=dPops["pvbasket"],
                                         ncons=dNconns["proj_poolosyn_to_pvbasket"],
                                         post_seg_group="apical_list_100_to_1000",
                                         weight_mult=dWeightMults["proj_poolosyn_to_pvbasket"])
    if proj_poolosyn_to_pvbasket:
        total_cons += len(proj_poolosyn_to_pvbasket[0].connection_wds)                                           
    proj_pvbasket_to_poolosyn = add_proj(network,
                                         prepop=dPops["pvbasket"], postpop=dPops["poolosyn"],
                                         ncons=dNconns["proj_pvbasket_to_poolosyn"],
                                         post_seg_group="soma_group",
                                         weight_mult=dWeightMults["proj_pvbasket_to_poolosyn"])
    if proj_pvbasket_to_poolosyn:
        total_cons += len(proj_pvbasket_to_poolosyn[0].connection_wds)                                           
    proj_pvbasket_to_pvbasket = add_proj(network,
                                         prepop=dPops["pvbasket"], postpop=dPops["pvbasket"],
                                         ncons=dNconns["proj_pvbasket_to_pvbasket"],
                                         post_seg_group="soma_group",
                                         weight_mult=dWeightMults["proj_pvbasket_to_pvbasket"])
    if proj_pvbasket_to_pvbasket:
        total_cons += len(proj_pvbasket_to_pvbasket[0].connection_wds)
        
    print("number of connections: %i (outer stimulation not included)"%total_cons)
    
    proj_ca3_to_poolosyn = add_proj(network,
                                    prepop=pop_ca3, postpop=dPops["poolosyn"],
                                    ncons=dNconns["proj_ca3_to_poolosyn"],
                                    post_seg_group="dendrite_list_50_to_200",
                                    weight_mult=dWeightMults["proj_ca3_to_poolosyn"])
    proj_ec_to_poolosyn = add_proj(network,
                                   prepop=pop_ec, postpop=dPops["poolosyn"],
                                   ncons=dNconns["proj_ec_to_poolosyn"],
                                   post_seg_group="dendrite_list_200_to_1000",
                                   weight_mult=dWeightMults["proj_ec_to_poolosyn"])
    proj_ca3_to_pvbasket = add_proj(network,
                                    prepop=pop_ca3, postpop=dPops["pvbasket"],
                                    ncons=dNconns["proj_ca3_to_pvbasket"],
                                    post_seg_group="dendrite_list_50_to_200",
                                    weight_mult=dWeightMults["proj_ca3_to_pvbasket"])                       
                                            
    # save to file
    nml_fName = "%s.net.nml"%network.id + (".h5" if format_=="hdf5" else "")
    oc.save_network(nml_doc, nml_fName,
                    validate=(format_=='xml'), format=format_, 
                    use_subfolder=False,target_dir=target_dir)
    
    if generate_LEMS:
    
        # create display for both population (+ specify saving)
        mt_ = 5  # max traces to display and save
        displays = {}; save_traces = {}; save_spikes = {}     
        for cell_type, pop in dPops.iteritems():  # stim pops not included
            d_ = "Display_%s_v"%pop.id
            displays[d_] = []
            f_ = "Sim_%s.%s.v.dat"%(nml_doc.id, pop.id)           
            save_traces[f_] = []
            s_ = "Sim_%s.%s.spikes"%(nml_doc.id, pop.id)
            save_spikes[s_] = []
            max_traces = mt_ if pop.get_size() >= mt_ else pop.get_size()
            for i in range(0, max_traces):
                quantity = "%s/%i/%s/v"%(pop.id, i, pop.component)
                displays[d_].append(quantity)
                save_traces[f_].append(quantity)
                save_spikes[s_].append("%s/%i/%s"%(pop.id, i, pop.component))
        
        lems_fName = oc.generate_lems_simulation(nml_doc, network, 
                                                 target_dir+'/'+nml_fName,
                                                 duration=duration, dt=dt,
                                                 gen_plots_for_all_v=False,
                                                 gen_plots_for_quantities=displays,
                                                 gen_saves_for_all_v=False,  # don't try to save tsince for ca3, ec
                                                 gen_saves_for_quantities=save_traces,
                                                 gen_spike_saves_for_all_somas=False,
                                                 gen_spike_saves_for_only_populations=[pop_poolosyn.id, pop_pvbasket.id],
                                                 #gen_spike_saves_for_cells=save_spikes,
                                                 lems_file_name="LEMS_%s%s.xml"%(network.id,".h5" if format_=="hdf5" else ""),
                                                 include_extra_lems_files=["PyNN.xml"],  # to include SpikeSourcePoisson
                                                 simulation_seed=simulation_seed,
                                                 target_dir=target_dir)
                                                 
    else:
        lems_fName = None
        
    return lems_fName
     

def generate_instance(scaling, 
                      simduration, 
                      format_, 
                      run_simulation, 
                      simulator, 
                      target_dir,
                      simulation_seed=12345,
                      network_seed=12345):
    """helper function to make automated testing easier"""

    rate = 10
    dt = 0.01  # ms

    dPopsize = {"poolosyn":scale(50, scaling), "pvbasket":scale(20, scaling), "stim":scale(40, scaling)}

    dNconns = {"proj_poolosyn_to_pvbasket":30, "proj_pvbasket_to_poolosyn":18, "proj_pvbasket_to_pvbasket":18,
               "proj_ca3_to_poolosyn":50, "proj_ec_to_poolosyn":30, "proj_ca3_to_pvbasket":40}

    dWeightMults = {"proj_poolosyn_to_pvbasket":20, "proj_pvbasket_to_poolosyn":20, "proj_pvbasket_to_pvbasket":50,
                    "proj_ca3_to_poolosyn":50, "proj_ec_to_poolosyn":15, "proj_ca3_to_pvbasket":15}

    reference = "PINGNet"
    if scaling != 1:
        reference += ("_%s"%scaling).replace(".","_")       
    lems_fName = generate_PING_net(reference, dPopsize, dNconns, dWeightMults, rate,
                                   generate_LEMS=True, duration=simduration, dt=dt,
                                   format_=format_, target_dir=target_dir,
                                   simulation_seed=simulation_seed,
                                   network_seed=network_seed)

    if lems_fName and run_simulation:
        if simulator == "NEURON":
            oc.simulate_network(lems_fName, simulator="jNeuroML_%s"%simulator,
                                max_memory="5G")
        elif simulator == "NetPyNE":
            import multiprocessing as mp
            oc.simulate_network(lems_fName, simulator="jNeuroML_%s"%simulator,
                                max_memory="5G", num_processors=mp.cpu_count())

            # analyse saved results
            from analyse_PING import *                             
            dTraces = {}; dSpikeTimes = {}; dSpikingNeurons = {}
            for cell_type in ["poolosyn", "pvbasket"]:
                t, traces = get_traces("Sim_%s.%scell.v.dat"%(reference, cell_type), simduration, dt)
                dTraces[cell_type] = traces[0, :]
                spikeTimes, spikingNeurons, _ = get_spikes_rate("Sim_%s.pop_%s.spikes"%(reference, cell_type), t, dPopsize[cell_type])
                dSpikeTimes[cell_type] = spikeTimes; dSpikingNeurons[cell_type] = spikingNeurons

                plot_rasters(dSpikeTimes, dSpikingNeurons, simduration=t[-1], saveName=reference)
                plot_traces(t, dTraces, saveName=reference)
        else:
            raise Exception("simulator:%s is not yet implemented"%simulator)



if __name__ == "__main__":
    
    if len(sys.argv) > 1:    
        if sys.argv[1] == "-test":
            
            generate_instance(0.1, 80, "xml",  False, "NEURON", "./",simulation_seed=1111,network_seed=12345)  # scaled down by 10
            generate_instance(0.1, 80, "hdf5", False, "NEURON", "./",simulation_seed=1111,network_seed=12345)  # scaled down by 10
            generate_instance(10,  100, "hdf5", False, "NEURON", "./")  # scaled up by 10

            exit()
            
        else:
            run_simulation = sys.argv[1]
            try:
                simulator = sys.argv[2]
            except:
                simulator = "NEURON"
    else:
        run_simulation = False
        simulator = "NEURON"

    scaling = 0.1
    simduration = 100  # ms
    format_ = "xml"

    generate_instance(scaling, simduration, format_, run_simulation, simulator, "./")
        
