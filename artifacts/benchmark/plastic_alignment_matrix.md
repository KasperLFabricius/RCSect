# Plastic alignment matrix

| category | item | status | implementation_note | source_location |
| --- | --- | --- | --- | --- |
| Sign conventions | axial load | aligned | P_target and N_calc are compression-positive | core/solver_conventions.py:to_compression_positive |
| Sign conventions | strain_concrete reporting | aligned | single reported-strain conversion helper | core/solver_conventions.py:format_reported_strain |
| Sign conventions | strain_mild reporting | not aligned | governing bar total strain via shared formatter | core/solver_plastic.py:build_reported_outputs |
| Sign conventions | strain_prestressed reporting | not aligned | governing bar total strain via shared formatter | core/solver_plastic.py:build_reported_outputs |
| Sign conventions | Mx/My | partially aligned | single moment local->global transform | core/solver_conventions.py:rotate_moment_local_to_global |
| Sign conventions | DX/DY | not aligned | single arm vector local->global transform | core/solver_conventions.py:rotate_vector_local_to_global |
| Orientation conventions | V definition | aligned | V is NA relative to global +Y | core/solver_conventions.py:ANGLE_CONVENTION |
| Orientation conventions | rotation direction | aligned | local_rotation_deg is single source for angle | core/solver_plastic.py:_assemble_solution |
| Orientation conventions | local/global Mx/My transform | aligned | shared helper used | core/solver_conventions.py:rotate_moment_local_to_global |
| Orientation conventions | local/global DX/DY transform | aligned | shared helper used | core/solver_conventions.py:rotate_vector_local_to_global |
| Factor semantics | gamma_c | aligned | reduces concrete stress ordinate | core/materials.py:ConcreteType1 |
| Factor semantics | gamma_y | aligned | reduces yield/design stress | core/materials.py |
| Factor semantics | gamma_u | aligned | reduces terminal/rupture stress where needed | core/materials.py |
| Factor semantics | gamma_E | aligned | reduces modulus | core/materials.py |
| Factor semantics | IS / eps0 handling | aligned | prestress initial strain added before constitutive eval | core/solver_plastic.py:_calculate_detailed_internal_forces |
| Material-family implementation | concrete type 1 | aligned | percent-strain polynomial + plateau; tension=0 | core/materials.py:ConcreteType1.stress |
| Material-family implementation | mild steel type 1 | aligned | piecewise elastic/yield/hardening tension and plastic compression | core/materials.py:MildSteelType1.stress |
| Material-family implementation | prestressed steel type 1 | aligned | tension-side-only piecewise in percent strain | core/materials.py:PrestressedSteelType1.stress |
| Material-family implementation | prestressed steel type 6 | aligned | tension-side-only elastic+hardening | core/materials.py:PrestressedSteelType6.stress |
| Reported outputs | strain_concrete | aligned | centralized in build_reported_outputs | core/solver_plastic.py:build_reported_outputs |
| Reported outputs | strain_mild | not aligned | centralized in build_reported_outputs | core/solver_plastic.py:build_reported_outputs |
| Reported outputs | strain_prestressed | not aligned | centralized in build_reported_outputs | core/solver_plastic.py:build_reported_outputs |
| Reported outputs | compress_force | aligned | zone compression concrete+mild+prestress | core/solver_plastic.py:build_reported_outputs |
| Reported outputs | L | not aligned | from centroid arm vector magnitude | core/solver_plastic.py:build_reported_outputs |
| Reported outputs | DX | not aligned | from centroid arm vector | core/solver_plastic.py:build_reported_outputs |
| Reported outputs | DY | not aligned | from centroid arm vector | core/solver_plastic.py:build_reported_outputs |
| Reported outputs | warning | partially aligned | single compression-rebar vs concrete-capacity rule | core/solver_plastic.py:build_reported_outputs |
| Reported outputs | NA intersections | aligned | from y_na and shared orientation angle | core/solver_plastic.py:_assemble_solution |
| Reported outputs | U / R | partially aligned | U maps to y_na; R unresolved by current corpus | tests/plastic_diagnostics.py |
| Geometry semantics | outer winding | partially aligned | relies on input geometry; not re-oriented here | core/geometry.py |
| Geometry semantics | inner winding | partially aligned | relies on input geometry; not re-oriented here | core/geometry.py |
| Geometry semantics | zone classification methodology | aligned | solved strain-field classification helper | core/solver_conventions.py:classify_zone_from_total_strain |
