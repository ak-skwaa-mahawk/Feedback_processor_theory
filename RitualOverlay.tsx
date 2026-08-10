import { playBreathStart, playUncoilCue, playRitualSuccess, playRitualCancel } from "../utils/hapticsPlayer";

useEffect(() => {
  if (visible) {
    logger.info("Revocation ritual started");
    playBreathStart();

    breathRef.current?.play();

    const uncoilTimer = setTimeout(() => {
      logger.sovereign("Breath complete — uncoiling");
      playUncoilCue();
      coilRef.current?.play(0, 180);
    }, 4000);

    return () => clearTimeout(uncoilTimer);
  }
}, [visible]);

const handleCoilFinish = () => {
  logger.sovereign("Ritual complete");
  playRitualSuccess();
  onComplete();
};

const handleCancel = () => {
  logger.info("Ritual cancelled");
  playRitualCancel();
  onCancel();
};