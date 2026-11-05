import cadquery as cq

from open_cane import CaneJoint, CaneTip

if __name__ == "__main__":
    joint = CaneJoint()
    tip = CaneTip(joint)
    model = tip.get_shape()
    cq.exporters.export(model, "tip.stl")
