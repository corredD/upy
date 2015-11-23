
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/nma.py is part of upy.

    upy is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    upy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with upy.  If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.
"""
from prody import *
import sys
import getopt

def computeNormalMode(userfilenamein="",userfilenameout="NMA.pdb", 
                      usermode=0,userrmsd=0.8, usernbconf=5, 
                      conf="allatom", usercutoff=15.0, usergamma=1.0) : 
	mystruct = parsePDB(userfilenamein, model=1)
	mystruct_ca = mystruct.select('protein and name CA')

	anm = ANM(userfilenamein+str(usermode))
	anm.buildHessian(mystruct_ca, gamma=usergamma, cutoff=usercutoff)
	anm.calcModes()
	
	bb_anm, bb_atoms = extrapolateModel(anm, mystruct_ca, mystruct.select(conf))
	ensemble = sampleModes(bb_anm[usermode], bb_atoms, n_confs=usernbconf, rmsd=userrmsd)
	nmastruct = mystruct.copy( bb_atoms )
	nmastruct.addCoordset(ensemble)
			
	writePDB(userfilenameout, nmastruct)

def usage() :
	print "Compute a normal mode analysis based on Anistropic Network Model (ANM) on alpha carbon, according to minimized input pdb struture (local file or pdb code) and provide an output pdb structure with trajectory the specified normal mode, using extrapolation to produce a carbon alpha trajectory, a backbone trajectory, or a all atom trajectory (default)"
	print "python nma.py --input=input.pdb -output=output.pdb -mode=mode [--rmsd=0.8][--nbconformations=5][gamma=][cutoff=][--all][--calpha][--backbone]"
		
def main():
	try : 
		opts, args = getopt.getopt(sys.argv[1:], "hi:o:m:r:n:g:c:", ["help","input=", "output=","mode=", "rmsd=","nbconformations=", "gamma=", "cutoff=", "backbone", "calpha", "all"])
	except getopt.GetoptError:
		usage()
		sys.exit(2)	
	mode = 0
	rmsd = 0.8
	nbconformations = 5
	pdbin=""
	pdbout=""
	conf="all"
	gamma=1.0
	cutoff=15.0
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()               
			sys.exit()                  
		elif opt in ("-i", "--input"): 
			pdbin = arg   
		elif opt in ("-o", "--output"): 
			pdbout = arg   
		elif opt in ("-r", "--rmsd"): 
			rmsd = float(arg)   
		elif opt in ("-n", "--nbconformations"):
			nbconformations = int(arg)
		elif opt in ("-c", "--cutoff"):
			cutoff = float(arg)
		elif opt in ("-g", "--gamma"):
			gamma = float(arg)
		elif opt in ("-m", "--mode"): 
			mode = int(arg)
		elif opt in ("--allatom"): 
			conf = "all"
		elif opt in ("--calpha"): 
			conf = "calpha"
		elif opt in ("--backbone"): 
			conf = "backbone"
		else : 
			usage()
			sys.exit(2)	
	if pdbin=="" or pdbout=="" or mode==0 : 
			usage()
			sys.exit(2)	
	else : 		
		computeNormalMode(pdbin,pdbout, mode, rmsd, nbconformations, conf, cutoff, gamma)

if __name__ == "__main__":
    sys.exit(main())