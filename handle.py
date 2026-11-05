from open_cane import CaneHandle, CaneJoint

if __name__ == "__main__":
    joint = CaneJoint()
    handle = CaneHandle(joint)
    model = handle.get_shape()
    model.export("handle.step")
