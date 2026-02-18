# PVmizer Geo – Key Learnings

## Texture Loading
- Texture dir is `textures/` at project root, NOT `PVmizer GEO/textures/`
- Concrete roof classes (flat/gable/pyramid/hip) must use `texture_base_path = "textures"`
- `texture_manager.py` searches multiple fallback dirs and correctly resolves `textures/`
- Correct filename: `rooftile.jpg` (not `roof_tiles.jpg`)
- Ground must use `pv.Plane` for texture coords to work — `delaunay_2d()` reorders points and breaks UV mapping

## Ground Planes
- ModelTab previously created a plain green plane at z=0 that covered the EnvironmentManager grass at z=-0.05
- Solution: removed ModelTab's `_create_single_ground_plane()` call; EnvironmentManager owns the ground
- EnvironmentManager uses `pv.Plane(i_resolution=20, j_resolution=20)` with tiled UVs

## Performance
- Do NOT call `enable_shadows()`, `enable_depth_peeling()`, `enable_anti_aliasing()` on the plotter — very expensive
- Do NOT use `delaunay_2d()` for ground mesh — use `pv.Plane` instead
- Do NOT add individual debug spheres per attachment point — use a single point cloud actor

## Axes / Grid
- Remove `show_axes()` and `show_grid()` from model_tab.py
- Remove `add_axes()` from base_roof.py

## Tree/Pole Placement
- The right-click interactive placement mode (prepare_tree_placement + VTK RightButtonPressEvent) is unreliable in Qt
- Solution: buttons directly emit `add_tree` / `add_pole` to place at a random free attachment point
- Attachment point rings must respect `min_safe_radius = sqrt((L/2)²+(W/2)²) + 1.5` to avoid spawning inside building

## Duplicate Methods
- `environment_manager.py` had duplicate `show_environment_attachment_points` and `hide_environment_attachment_points`; Python uses the LAST definition — always check for duplicates
