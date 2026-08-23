(()=>{
'use strict';
/*
 * Legacy share-impact renderer intentionally disabled.
 *
 * The Forge collision engine now owns share-event particles and counter glow.
 * Keeping this legacy burst active caused exactly the unwanted behaviour where
 * the counter glowed for the whole share burst instead of reacting to each
 * individual particle arrival.
 *
 * Kept as a compatibility stub because dashboard_v4_forge_collision.js is
 * injected after this asset by the build patch.
 */
if(window.__FIXEDCOIN_SHARE_IMPACT_LEGACY_DISABLED__) return;
window.__FIXEDCOIN_SHARE_IMPACT_LEGACY_DISABLED__=true;
})();
