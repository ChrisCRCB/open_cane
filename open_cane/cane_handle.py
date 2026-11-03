from dataclasses import dataclass

import cadquery as cq

from .braille import BrailleLine
from .cane_joint import CaneJoint


@dataclass(frozen=True)
class CaneHandle:
    """The handle of the cane."""

    joint: CaneJoint
    """The joint whose dimensions will be used."""

    handle_length: float = 190
    """The length of the handle."""

    top_thickness: float = 20
    """How much material will make up the top of the handle."""

    braille_text: str | None = "⠠⠕⠏⠢⠀⠠⠉⠁⠝⠑"
    """The braille to render on the handle."""

    grip_fillet: float = 2
    """How much to fillet the flat surface of the grip."""

    @property
    def braille(self) -> cq.Compound | None:
        """The braille to add to the handle."""
        text = self.braille_text
        if text is None:
            return None
        return BrailleLine(line=text).get_shape()

    def get_shape(self) -> cq.Workplane:
        """Get the shape of the handle."""
        join_length = self.joint.wide_join_length
        height = self.handle_length + join_length + self.top_thickness
        cross_section = self.joint.wall_thickness + self.joint.tube_radius
        box_y = cross_section * 2
        cylinder = cq.Workplane("XY").cylinder(
            height, cross_section, centered=(True, True, False)
        )
        box = (
            cq.Workplane("XY")
            .box(height, box_y, cross_section, centered=(False, True, False))
            .edges(">Z and |X")
            .fillet(self.grip_fillet)
        )
        box = box.rotate((0, 0, 0), (0, 1, 0), 270)
        cylinder = cylinder.union(box)
        # An exact-radius fillet degenerates at the top face.
        cylinder = cylinder.edges(">Z").fillet(cross_section * 0.999)
        braille = self.braille
        if braille is not None:
            bounds = braille.BoundingBox()
            if bounds.xlen > height or bounds.ylen > box_y:
                raise RuntimeError(
                    f"Braille text ({bounds.xlen} x {bounds.ylen}) does not fit on the handle ({height} x {box_y})."
                )
            center_x = (bounds.xmin + bounds.xmax) / 2
            center_y = (bounds.ymin + bounds.ymax) / 2
            braille = braille.rotate((0, 0, 0), (0, 1, 0), 270)
            rotated_bounds = braille.BoundingBox()
            braille = braille.translate(
                (
                    -cross_section - rotated_bounds.xmax,
                    -center_y,
                    height / 2 - center_x,
                )
            )
            cylinder = cylinder.union(braille)
        middle = (
            cq.Workplane("XY")
            .cylinder(
                join_length,
                self.joint.tube_radius,
                centered=(True, True, False),
            )
            .union(
                cq.Workplane("XY").cylinder(
                    height, self.joint.string_hole_radius, centered=(True, True, False)
                )
            )
        )
        cylinder = cylinder.cut(middle)
        return cylinder.edges("<Z").fillet(self.joint.fillet)
