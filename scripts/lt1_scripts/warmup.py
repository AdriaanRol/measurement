try:
    ADwin_pos.move_abs_xyz(0,0,0)
except NameError:
    print "Adwin _pos failed"
    pass
AttoPositioner.PositionerAmplitude(0,25000)
AttoPositioner.PositionerAmplitude(1,25000)
AttoPositioner.PositionerAmplitude(2,25000)
AttoPositioner.PositionerFrequency(0,100)
AttoPositioner.PositionerFrequency(1,100)
AttoPositioner.PositionerFrequency(2,100)
AttoPositioner.PositionerDCLevel(0,0)
AttoPositioner.PositionerDCLevel(1,0)
AttoPositioner.PositionerDCLevel(2,0)
AttoPositioner.PositionerDCLevel(3,0)
AttoPositioner.PositionerDCLevel(4,0)
AttoPositioner.PositionerDCLevel(5,0)
AttoPositioner.PositionerDcInEnable(3,0)
AttoPositioner.PositionerDcInEnable(4,0)
AttoPositioner.PositionerDcInEnable(5,0)
