from dataclasses import dataclass

import cadquery as cq


@dataclass(frozen=True)
class CaneJoint:
    """A joint between two metal tubes."""

    tube_radius: float = 6.6
    """The radius of the metal tube, plus some.

    For example, with 13 mm tubes, the radius is `6.5`. Then add a little for wiggle room.

    This value will form the radius of the wider join.
    """

    wall_thickness: float = 3
    """The thickness of the walls."""

    wide_join_length: float = 40
    """The length of the part of the joint where the rod fits."""

    string_hole_length: float = 5
    """The length of the part where the string passes through."""

    string_hole_radius: float = 2.9
    """The radius of the hole where the string will pass through."""

    narrow_join_length: float = 40
    """The length of the part which will clamp the tube."""

    narrow_join_offset: float = 0.2
    """The offset from `tube_radius` which will inform the radius of the part of the join which grips the tube."""

    fillet: float = 1
    """The fillet for the two ends."""

    @property
    def full_length(self) -> float:
        """The full length of the section."""
        return self.wide_join_length + self.string_hole_length + self.narrow_join_length

    @property
    def full_radius(self) -> float:
        """Return the radius of the join."""
        return self.tube_radius + self.wall_thickness

    @property
    def wide_section(self) -> cq.Workplane:
        """The wider part of the join.

        This value should be cut away from the eventual solid."""
        return cq.Workplane("XY").cylinder(
            self.wide_join_length, self.tube_radius, centered=(True, True, False)
        )

    @property
    def narrow_join_radius(self) -> float:
        """The radius of the narrow joint."""
        return self.tube_radius - self.narrow_join_offset

    @property
    def narrow_section(self) -> cq.Workplane:
        """The narrower part of the join.

        This section should be cut away from the eventual solid, and will be used to grip the inner metal tube.
        """
        return cq.Workplane("XY").cylinder(
            self.narrow_join_length,
            self.narrow_join_radius,
            centered=(True, True, False),
        )

    @property
    def string_hole(self) -> cq.Workplane:
        """The hole which the string will pass through.

        This model should be cut from the eventual solid.
        """
        return cq.Workplane("XY").cylinder(
            self.string_hole_length,
            self.string_hole_radius,
            centered=(True, True, False),
        )

    def get_shape(self) -> cq.Workplane:
        """Get the entire model."""
        cylinder = cq.Workplane("XY").cylinder(
            self.full_length, self.full_radius, centered=(True, True, False)
        )
        wide_cylinder = self.wide_section
        cylinder = cylinder.cut(
            wide_cylinder.translate(
                (0, 0, self.narrow_join_length + self.string_hole_length)
            )
        )
        string_hole = self.string_hole
        cylinder = cylinder.cut(string_hole.translate((0, 0, self.narrow_join_length)))
        narrow_cylinder = self.narrow_section
        cylinder = cylinder.cut(narrow_cylinder)
        return cylinder.edges("<Z or >Z").fillet(self.fillet)
