import base64
import hashlib
import json
import re

from conftest import write_cube_stl
from print3d.viewer import MODULES, VENDOR, build_viewer


def _data(page: str) -> dict:
    start = page.index('id="data">') + len('id="data">')
    return json.loads(page[start:page.index("</script>", start)])


def test_one_part_carries_its_mesh_and_numbers(tmp_path):
    job = tmp_path / "plate"
    stl = write_cube_stl(job / "mesh" / "plate.stl")
    report = {
        "brief": {"prompt": "a plate </script> test", "color_name": "red"},
        "mesh_metrics": {"size_mm": [20, 20, 20]},
        "slice_metrics": {"estimated_minutes": 12.5, "filament_g": 3.1},
    }
    viewer = build_viewer(job, report)
    assert viewer == job / "view.html"
    data = _data(viewer.read_text())
    assert data["title"] == "a plate </script> test"
    assert (data["minutes"], data["grams"]) == (12.5, 3.1)
    [part] = data["parts"]
    assert part["color"] == "red" and part["hex"].startswith("#")
    assert base64.b64decode(part["stl"]) == stl.read_bytes()


def test_parts_come_assembled_with_their_groups(tmp_path):
    job = tmp_path / "box"
    for name in ("body", "lid", "mark"):
        write_cube_stl(job / "mesh" / "assembly" / f"{name}.stl")
    report = {
        "brief": {"prompt": "box"},
        "parts": [
            {"name": "body", "object": "body", "color": "white"},
            {"name": "lid", "object": "lid", "color": "white"},
            {"name": "mark", "object": "lid", "color": "black"},
        ],
    }
    data = _data(build_viewer(job, report).read_text())
    assert [(p["name"], p["group"]) for p in data["parts"]] == [("body", "body"), ("lid", "lid"), ("mark", "lid")]


def test_no_mesh_no_viewer(tmp_path):
    report = {"brief": {"prompt": "x"}, "mesh_metrics": {"size_mm": [1, 1, 1]}}
    assert build_viewer(tmp_path / "empty", report) is None


def test_panel_folds_and_starts_folded_in_a_narrow_pane(tmp_path):
    job = tmp_path / "plate"
    write_cube_stl(job / "mesh" / "plate.stl")
    page = build_viewer(job, {"brief": {"prompt": "plate"}, "mesh_metrics": {"size_mm": [20, 20, 20]}}).read_text()
    assert '<details id="panel" open>' in page and "<summary>" in page
    assert "window.innerWidth >= 700" in page


def test_measure_between_two_clicks(tmp_path):
    job = tmp_path / "plate"
    write_cube_stl(job / "mesh" / "plate.stl")
    page = build_viewer(job, {"brief": {"prompt": "plate"}, "mesh_metrics": {"size_mm": [20, 20, 20]}}).read_text()
    assert '<button id="measure" aria-pressed="false">Measure</button>' in page
    assert '<div id="readout" hidden></div>' in page


def _importmap(page: str) -> dict:
    start = page.index('<script type="importmap">') + len('<script type="importmap">')
    return json.loads(page[start:page.index("</script>", start)])


def test_three_is_inline_so_the_page_opens_offline(tmp_path):
    job = tmp_path / "plate"
    write_cube_stl(job / "mesh" / "plate.stl")
    page = build_viewer(job, {"brief": {"prompt": "plate"}, "mesh_metrics": {"size_mm": [20, 20, 20]}}).read_text()
    imports = _importmap(page)["imports"]
    # Every specifier the module imports resolves to a vendored file carried in the page.
    used = set(re.findall(r"^import .* from '([^']+)';$", page, re.M))
    assert used == set(imports) == set(MODULES)
    for spec, name in MODULES.items():
        prefix = "data:text/javascript;base64,"
        assert imports[spec].startswith(prefix)
        assert base64.b64decode(imports[spec][len(prefix):]) == (VENDOR / name).read_bytes()
    assert "://" not in page  # nothing fetched from anywhere (base64 has no colon)


def test_vendored_three_is_the_pinned_release():
    pinned = {
        "three.module.min.js": "3e690ac7d180b0aadf0891bea39eec643e29e2d3e75c99b18689518665f69ba6",
        "OrbitControls.js": "5a44a9e86a2a0fb11933eed69bc2cd33c76a496854c1aed6ed776efa87d7b064",
        "STLLoader.js": "896d006a48b8f125385a485ccae154dadee801a953f0b45ceffe7ddd8a29ca93",
        "LICENSE": "852e0e8699169bf9f6fdc6bda3e682d078dcbc738b5d33e74df594721bff271d",
    }
    assert {name: hashlib.sha256((VENDOR / name).read_bytes()).hexdigest() for name in pinned} == pinned
