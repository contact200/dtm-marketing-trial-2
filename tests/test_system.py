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
            self.assertTrue(all(x[k] for k in ("hook","second","third","closing","caption")))
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
    def test_new_run_always_changes_auto_concept(self):
        picks=[render.select_campaign(self.c,"auto","2026-11-23",sequence) for sequence in range(28)]
        self.assertEqual(len(set(x["id"] for x in picks[:7])),7)
        self.assertEqual(picks[0]["id"],picks[7]["id"])
        self.assertNotEqual(picks[0]["id"],picks[1]["id"])
    def test_four_fast_beats(self):
        self.assertEqual([render.scene_for(t,13)[0] for t in (0.4,3.4,7.0,11.3)],[0,1,2,3])
    def test_clean_brand_visual_policy(self):
        self.assertEqual(self.brand["colors"]["royal_blue"].lower(),"#2453e7")
        self.assertIn("not slow",self.brand["style_spec"]["pacing"].lower())
        self.assertIn("no mountains",self.brand["style_spec"]["reference"].lower())
        banned=("bukowina","skiing","snowboarding","mountain retreat","winterscape")
        for c in self.c:
            script=" ".join(c[key] for key in ("hook","second","third","closing","caption")).lower()
            self.assertFalse(any(word in script for word in banned))
        for i in range(7):
            base=render.artwork_base(self.c[i]["theme"],360,640)
            self.assertEqual(base.getpixel((2,2)),render.COLORS["white"])
            frame=render.render_frame(base,self.c[i],self.brand,self.c[i]["theme"],360,640,10.2,13)
            self.assertEqual(frame.size,(360,640))
    def test_variants_tailored_to_each_concept(self):
        variants=json.loads((ROOT/"config/copy_variations.json").read_text())
        for k,vs in variants.items():
            self.assertEqual(len(vs),3)
            self.assertEqual(len({v["hook"] for v in vs}),3)
            for v in vs:
                self.assertTrue(all(v[field] for field in ("hook","second","third","closing","caption")))
                self.assertIn("datethemoment.com",v["caption"])
    def test_photo_opt_in(self):
        self.assertEqual(json.loads((ROOT/"config/photos.json").read_text())["photos"],[])
if __name__=="__main__":unittest.main()
