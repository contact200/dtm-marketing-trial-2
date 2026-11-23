import importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("render",ROOT/"scripts/render.py")
render=importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)
class StudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=json.loads((ROOT/"config/campaigns.json").read_text())
        cls.brand=json.loads((ROOT/"config/brand.json").read_text())
    def test_concept_families(self):
        self.assertEqual(len(self.c),7)
        self.assertEqual(len(set(x["theme"] for x in self.c)),7)
    def test_copy(self):
        for x in self.c:
            self.assertIn("datethemoment.com",x["caption"])
            self.assertTrue(all(x[k] for k in ("hook","second","closing","caption")))
    def test_variants(self):
        v=json.loads((ROOT/"config/copy_variations.json").read_text())
        self.assertTrue(all(len(v[x["id"]])==3 for x in self.c))
    def test_stable_rotation(self):
        self.assertEqual(render.select_campaign(self.c,"auto","2026-11-23")["id"],render.select_campaign(self.c,"auto","2026-11-23")["id"])
        self.assertNotEqual(render.select_campaign(self.c,"auto","2026-11-23")["id"],render.select_campaign(self.c,"auto","2026-11-25")["id"])
    def test_artwork(self):
        for x in self.c:
            base=render.artwork_base(x["theme"],360,640)
            out=render.render_frame(base,x,self.brand,x["theme"],360,640,1.5,5.0)
            self.assertEqual(out.size,(360,640))
    def test_photo_opt_in(self):
        self.assertEqual(json.loads((ROOT/"config/photos.json").read_text())["photos"],[])
if __name__=="__main__":unittest.main()
