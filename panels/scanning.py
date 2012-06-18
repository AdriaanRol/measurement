# User configuration for at startup
# Copied from rt II
# MAY NOT WORK YET!!!!

# add_panel(your_panel_class, option1, option2, ...)

from counters import CounterPanel
add_panel(CounterPanel, title='Counters', sampling=100, ins='counters')

from scan2d import Scan2dPanel

add_panel(Scan2dPanel, title='Stage scan',
    sampling=500, ins='scan2d_stage')

add_panel(Scan2dPanel, title='Detection SM scan',
          sampling=500, ins='scan2d_det_sm')

# add_panel(Scan2dPanel, title='Back SM scan',
#           sampling=500, ins='scan2d_back_sm')
# 

from rt2_coordinator import RT2CoordinatorPanel
add_panel(RT2CoordinatorPanel, title='Control Panel', ins='setup_controller')

from optimize1d_counts_panel import Optimize1dCountsPanel
add_panel(Optimize1dCountsPanel, title='Optimize z front', ins='opt1d_counts',
        dimension='front_z')
add_panel(Optimize1dCountsPanel, title='Optimize Stage x', ins='opt1d_counts',
        dimension='stage_x')
add_panel(Optimize1dCountsPanel, title='Optimize Stage y', ins='opt1d_counts',
        dimension='stage_y')
add_panel(Optimize1dCountsPanel, title='Optimize Det SM x', ins='opt1d_counts',
        dimension='detsm_x')
add_panel(Optimize1dCountsPanel, title='Optimize Det SM y', ins='opt1d_counts',
        dimension='detsm_y')


from power_panel import Power
add_panel(Power, title='Power monitor', ins='power_monitor')
