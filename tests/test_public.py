import unittest
from datetime import datetime,timezone
from decimal import Decimal
from aquaflow.api import AquaFlowService
from aquaflow.treatment.chlorine_ct import Segment
from aquaflow.network.isolation import Pipe
from aquaflow.meters.balance import Meter
from aquaflow.simulation.hydraulics import Node,Link,solve
class T(unittest.TestCase):
    def test_health(self):self.assertEqual(AquaFlowService().health()["runtime_dependencies"],0)
    def test_ct(self):self.assertTrue(AquaFlowService().ct([Segment(20,1,.8,20)],10))
    def test_isolation(self):
        self.assertEqual(AquaFlowService().isolate({"S","A","B"},[Pipe("1","S","A"),Pipe("2","A","B")],{"2"},{"S"}),{"B"})
    def test_balance(self):
        i=[Meter("i",Decimal(0),Decimal(20),Decimal(1))]
        o=[Meter("o",Decimal(0),Decimal(15),Decimal(1))]
        self.assertEqual(AquaFlowService().water_balance(i,o,Decimal(1)),Decimal(4))
    def test_solver(self):
        r=solve([Node("S",0,60),Node("A",5,None)],[Link("L","S","A",2)])
        self.assertTrue(r.converged)
if __name__=="__main__":unittest.main()
