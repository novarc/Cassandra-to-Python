from cassandra import *
from datetime import datetime

class Register_RA_manager(Role):
    def __init__(self, mgr2):
        super().__init__('Register-RA-manager', ['mgr2']) 
        self.mgr2 = mgr2
    
    def canActivate(self, mgr): # R1.1.1
        return {
        	(mgr, role) for mgr, role in hasActivated if 
        	role.name == "RA-manager"
        }
    
    #'R1.1.2'
    #canDeactivate(mgr, x, Register-RA-manager(mgr2)) <-
    #	hasActivated(mgr, RA-manager())
    
    #'R1.1.6'
    #isDeactivated(mgr, RA-manager()) <-
    #	isDeactivated(x, Register-RA-manager(mgr))

#'R1.1.3'
#RA-manager-regs(count<x>, mgr) <-
#	hasActivated(x, Register-RA-manager(mgr))

class RA_manager(Role):
    def __init__(self):
        super().__init__('RA-manager', []) 
    
    def canActivate(self, mgr): # R1.1.4
        return {
        	(x, role) for x, role in hasActivated if 
        	role.name == "Register-RA-manager" and 
        	role.mgr == mgr
        }
    
    #'R1.1.5'
    #canDeactivate(mgr, mgr, RA-manager()) <-
    #	

#'R1.2.1'
#canReqCred(x, "NHS".hasActivated(x, NHS-registration-authority(ra, start, end))) <-
#	ra = "RA-ADB"

class NHS_service(Role):
    def __init__(self):
        super().__init__('NHS-service', []) 
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, srv): # R1.2.2
        #todo: Not implemented: 0 hasAcs in a rule.
        #canActivate(srv, Registration-authority())
        pass
    
    def canActivate_2(self, srv): # R1.2.3
        #todo: Not implemented: 0 hasAcs in a rule.
        #srv = "Spine"
        pass

class Registration_authority(Role):
    def __init__(self):
        super().__init__('Registration-authority', []) 
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, ra): # R1.2.4
        return {
        	(x, role) for x, role in hasActivated if 
        	role.name == "NHS-registration-authority" and 
        	role.ra == ra
        }
    
    def canActivate_2(self, ra): # R1.2.5
        return {
        	(x, role) for x, role in hasActivated if 
        	role.name == "NHS-registration-authority" and 
        	role.ra == ra
        }

class NHS_clinician_cert(Role):
    def __init__(self, org, cli, spcty, start, end):
        super().__init__('NHS-clinician-cert', ['org', 'cli', 'spcty', 'start', 'end']) 
        self.org, self.cli, self.spcty, self.start, self.end = org, cli, spcty, start, end
    
    def canActivate(self, mgr): # R2.1.1
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(mgr, RA-manager())
        #hasActivated(y, NHS-health-org-cert(org, start2, end2))
        #start in [start2, end2]
        #end in [start2, end2]
        #start < end
        pass
    
    #'R2.1.2'
    #canDeactivate(mgr, x, NHS-clinician-cert(org, cli, spcty, start, end)) <-
    #	hasActivated(mgr, RA-manager())

#'R2.1.4'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-clinician-cert(org, cli, spcty, start, end))) <-
#	hasActivated(y, NHS-health-org-cert(org, start2, end2)), e = org, Current-time() in [start2, end2]

#'R2.1.5'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-clinician-cert(org, cli, spcty, start, end))) <-
#	canActivate(e, NHS-service())

#'R2.1.6'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-clinician-cert(org, cli, spcty, start, end))) <-
#	e = cli

class NHS_Caldicott_guardian_cert(Role):
    def __init__(self, org, cg, start, end):
        super().__init__('NHS-Caldicott-guardian-cert', ['org', 'cg', 'start', 'end']) 
        self.org, self.cg, self.start, self.end = org, cg, start, end
    
    def canActivate(self, mgr): # R2.2.1
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(mgr, RA-manager())
        #hasActivated(x, NHS-health-org-cert(org, start2, end2))
        #start in [start2, end2]
        #end in [start2, end2]
        #start < end
        pass
    
    #'R2.2.2'
    #canDeactivate(mgr, x, NHS-Caldicott-guardian-cert(org, cg, start, end)) <-
    #	hasActivated(mgr, RA-manager())

#'R2.2.4'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-Caldicott-guardian-cert(org, cg, start, end))) <-
#	e = cg

#'R2.2.5'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-Caldicott-guardian-cert(org, cg, start, end))) <-
#	hasActivated(y, NHS-health-org-cert(org, start2, end2)), e = org, Current-time() in [start2, end2]

#'R2.2.6'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-Caldicott-guardian-cert(org, cg, start, end))) <-
#	canActivate(e, NHS-service())

class NHS_health_org_cert(Role):
    def __init__(self, org, start, end):
        super().__init__('NHS-health-org-cert', ['org', 'start', 'end']) 
        self.org, self.start, self.end = org, start, end
    
    def canActivate(self, mgr): # R2.3.1
        return {
        	(mgr, role) for mgr, role in hasActivated if 
        	role.name == "RA-manager"
        }
    
    #'R2.3.2'
    #canDeactivate(mgr, x, NHS-health-org-cert(org, start, end)) <-
    #	hasActivated(mgr, RA-manager())
    
    #'R2.1.3'
    #isDeactivated(mgr, NHS-clinician-cert(org, cli, spcty, start, end)) <-
    #	isDeactivated(x, NHS-health-org-cert(org, start2, end2)), other-NHS-health-org-regs(n, x, org, start2, end2), n = 0, start in [start2, end2], end in [start2, end2], start < end
    
    #'R2.2.3'
    #isDeactivated(mgr, NHS-Caldicott-guardian-cert(org, cg, start, end)) <-
    #	isDeactivated(x, NHS-health-org-cert(org, start2, end2)), other-NHS-health-org-regs(n, x, org, start2, end2), start in [start2, end2], end in [start2, end2], start < end, n = 0

#'R2.3.3i'
#other-NHS-health-org-regs(count<y>, x, org, start, end) <-
#	hasActivated(y, NHS-health-org-cert(org, start2, end2)), start in [start2, end2], end in [start2, end2], start < end, x != y

#'R2.3.3ii'
#other-NHS-health-org-regs(count<y>, x, org, start, end) <-
#	hasActivated(y, NHS-health-org-cert(org, start2, end2)), start in [start2, end2], end in [start2, end2], start < end, start != start2

#'R2.3.3iii'
#other-NHS-health-org-regs(count<y>, x, org, start, end) <-
#	hasActivated(y, NHS-health-org-cert(org, start2, end2)), start in [start2, end2], end in [start2, end2], start < end, end != end2

#'R2.3.4'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org, start, end))) <-
#	hasActivated(y, NHS-Caldicott-guardian-cert(org, cg, start2, end2)), Current-time() in [start2, end2], e = cg

#'R2.3.5'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org, start, end))) <-
#	hasActivated(y, NHS-clinician-cert(org, cli, spcty, start2, end2)), Current-time() in [start2, end2], e = cli

#'R2.3.6'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org, start, end))) <-
#	e = org

#'R2.3.7'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org2, start, end))) <-
#	ra.hasActivated(y, NHS-health-org-cert(org, start2, end2)), canActivate(ra, Registration-authority()), e = org

#'R2.3.8'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org2, start, end))) <-
#	org@ra.hasActivated(y, NHS-health-org-cert(org, start2, end2)), canActivate(ra, Registration-authority()), e = org

#'R2.3.9'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org, start, end))) <-
#	canActivate(e, NHS-service())

class Workgroup_member(Role):
    def __init__(self, org, group, spcty):
        super().__init__('Workgroup-member', ['org', 'group', 'spcty']) 
        self.org, self.group, self.spcty = org, group, spcty
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, cli): # R3.1.1
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(x, NHS-health-org-cert(org, start, end))
        #org@org.hasActivated(x, Register-team-member(cli, group, spcty))
        #Current-time() in [start, end]
        pass
    
    def canActivate_2(self, cli): # R3.1.2
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(x, NHS-health-org-cert(org, start, end))
        #org@org.hasActivated(x, Register-ward-member(cli, group, spcty))
        #Current-time() in [start, end]
        pass

#'R3.1.3'
#canReqCred(spine, "RA-ADB".canActivate(cli, Workgroup-member(org, group, spcty))) <-
#	spine = "Spine"