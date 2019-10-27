from simtk.openmm import app
import simtk.openmm as mm
from simtk import unit

def MinimizedEnergy(filepath):
    prmtop = app.AmberPrmtopFile(f'{filepath}.prmtop')
    inpcrd = app.AmberInpcrdFile(f'{filepath}.inpcrd')
    system = prmtop.createSystem(implicitSolvent=app.GBn2,
                                 nonbondedMethod=app.CutoffNonPeriodic,
                                 nonbondedCutoff=1.0*unit.nanometers,
                                 constraints=app.HBonds,
                                 rigidWater=True,
                                 ewaldErrorTolerance=0.0005)

    integrator = mm.LangevinIntegrator(300*unit.kelvin,
                                       1.0/unit.picoseconds,
                                       2.0*unit.femtoseconds)
    integrator.setConstraintTolerance(0.00001)
    # TODO: This should just recognize whatever the computer is capable of, not force CUDA.
    platform = mm.Platform.getPlatformByName('CUDA')
    # TODO: I am not sure if mixed precision is necessary. It dramatically changes the results.
    properties = {'CudaPrecision': 'mixed'}
    
    simulation = app.Simulation(prmtop.topology, system, integrator, platform)
    simulation.context.setPositions(inpcrd.positions)
    
    simulation.minimizeEnergy()
    energy = simulation.context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoule/unit.mole)
    return energy


# def MinimizedEnergyWithParam(filepath):
#     prmtop = app.AmberPrmtopFile(f'{filepath}.prmtop')
#     inpcrd = app.AmberInpcrdFile(f'{filepath}.inpcrd')
#     system = prmtop.createSystem(implicitSolvent=app.GBn2,
#                                  nonbondedMethod=app.CutoffNonPeriodic,
#                                  nonbondedCutoff=1.0 * unit.nanometers,
#                                  constraints=app.HBonds,
#                                  rigidWater=True,
#                                  ewaldErrorTolerance=0.0005)
#
#     integrator = mm.LangevinIntegrator(300 * unit.kelvin,
#                                        1.0 / unit.picoseconds,
#                                        2.0 * unit.femtoseconds)
#     integrator.setConstraintTolerance(0.00001)
#     # TODO: This should just recognize whatever the computer is capable of, not force CUDA.
#     platform = mm.Platform.getPlatformByName('CUDA')
#     # TODO: I am not sure if mixed precision is necessary. It dramatically changes the results.
#     properties = {'CudaPrecision': 'mixed'}
#
#     simulation = app.Simulation(prmtop.topology, system, integrator, platform)
#     simulation.context.setPositions(inpcrd.positions)
#
#     simulation.minimizeEnergy()
#     energy = simulation.context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoule / unit.mole)
#     return energy