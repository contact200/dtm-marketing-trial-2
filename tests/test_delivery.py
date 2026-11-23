"""Protect the Make.com -> Telegram receiver contract."""
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("dtm_delivery",ROOT/"scripts/deliver.py")
delivery=importlib.util.module_from_spec(spec)
spec.loader.exec_module(delivery)

class MakeDeliveryTests(unittest.TestCase):
    def test_delivery_missing_secrets_keeps_artifact_and_marks_undelivered(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            (out/"payload.json").write_text("{}",encoding="utf-8")
            (out/"reel.mp4").write_bytes(b"video")
            with patch.dict(os.environ,{"DTM_TRIAL_DELIVER_TO_MAKE":"true"},clear=True),patch.object(sys,"argv",["deliver.py",tmp]),patch.object(delivery,"upload") as upload,patch.object(delivery.requests,"post") as send:
                delivery.main()
                report=json.loads((out/"delivery.json").read_text())
                self.assertEqual(report["status"],"configuration_required")
                self.assertFalse(report["delivered_to_make"])
                self.assertIn("DTM_TRIAL_MAKE_WEBHOOK_URL",report["missing_settings"])
                self.assertTrue((out/"reel.mp4").exists())
                upload.assert_not_called()
                send.assert_not_called()

    def test_existing_receiver_fields_sent_with_public_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            (out/"payload.json").write_text(json.dumps({
                "date":"2026-11-23","campaign_id":"calendar_fills",
                "concept_family":"calendar_fills","caption":"Social-ready caption",
                "source_attribution":["original abstract motion graphics"]
            }),encoding="utf-8")
            (out/"reel.mp4").write_bytes(b"test")
            (out/"cover.jpg").write_bytes(b"test")
            urls=["https://example.supabase.co/storage/v1/object/public/trial/video.mp4",
                  "https://example.supabase.co/storage/v1/object/public/trial/cover.jpg"]
            env={
                "DTM_TRIAL_DELIVER_TO_MAKE":"true",
                "DTM_TRIAL_SUPABASE_URL":"https://example.supabase.co",
                "DTM_TRIAL_SUPABASE_SERVICE_ROLE_KEY":"TEST_ONLY",
                "DTM_TRIAL_MAKE_WEBHOOK_URL":"https://example.invalid/webhook",
                "GITHUB_RUN_ID":"45101072570",
            }
            with patch.dict(os.environ,env,clear=True),patch.object(sys,"argv",["deliver.py",tmp]),patch.object(delivery,"upload",side_effect=urls),patch.object(delivery.requests,"post",return_value=Mock()) as send:
                delivery.main()
                outgoing=send.call_args.kwargs["json"]
                self.assertEqual(outgoing["concept_id"],"calendar_fills")
                self.assertEqual(outgoing["social_caption"],"Social-ready caption")
                self.assertEqual(outgoing["video_url"],urls[0])
                self.assertEqual(outgoing["cover_url"],urls[1])
                self.assertEqual(outgoing["render_run_id"],"45101072570")
                self.assertTrue(outgoing["approval_required"])
                self.assertEqual(outgoing["source"],"dtm-marketing-trial-2")
                report=json.loads((out/"delivery.json").read_text())
                self.assertEqual(report["status"],"sent_to_make")
                self.assertTrue(report["delivered_to_make"])
                self.assertFalse(report["telegram_delivery_verified"])
