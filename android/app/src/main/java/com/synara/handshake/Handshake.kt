package com.synara.handshake

import org.json.JSONObject
import java.security.MessageDigest
import java.io.File
import android.content.Context
import java.lang.System
import java.text.SimpleDateFormat
import java.util.Locale
import java.util.Date

object Handshake {

    private const val SAHNEUTI_SALT = "SAHNEUTI-1815-1900-99733Q"

    fun sha256Hex(input: ByteArray): String {
        val md = MessageDigest.getInstance("SHA-256")
        val digest = md.digest(input)
        return digest.joinToString("") { "%02x".format(it) }
    }

    /**
     * Creates and saves a sovereign receipt under Sahneuti-99733-Q Root
     * @param context Android Context (for file writing)
     * @param nodeId e.g. "CLUSTER-N-HUD" or "DAO-COUNCIL-9"
     * @param payload Any JSONObject (glyph vote, TREASURE payload, magnetic alignment, etc.)
     * @return The full signed receipt (and saved to /data/data/.../files/99733Q_Deeds/)
     */
    fun createReceipt(context: Context, nodeId: String, payload: JSONObject): JSONObject {
        val payloadBytes = payload.toString().toByteArray(Charsets.UTF_8)
        val hash = sha256Hex(payloadBytes + SAHNEUTI_SALT.toByteArray())

        val receipt = JSONObject().apply {
            put("root_authority", "Sahneuti-99733-Q")
            put("node_id", nodeId)
            put("ts", System.currentTimeMillis() / 1000)
            put("sahneuti_salt", SAHNEUTI_SALT)
            put("payload_hash", hash)
            put("payload", payload)
            put("signature", "0x$hash-SAHNEUTI-ROOT")
            put("manifest_version", "11D-Conscious-Jump • March 5, 2026")
        }

        // Save to private app storage (survives app kill)
        val deedsDir = File(context.filesDir, "99733Q_Deeds")
        if (!deedsDir.exists()) deedsDir.mkdirs()

        val timestampStr = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
        val file = File(deedsDir, "99733Q_Receipt_${nodeId}_$timestampStr.json")
        file.writeText(receipt.toString(2))

        // Optional: Trigger acoustic confirmation or Cluster N HUD here
        // (e.g. call your acoustic bridge or launch SovereignCompass)

        return receipt
    }
}

val payload = JSONObject().apply {
    put("glyphs_received", 9)
    put("resonance", 1.00)
    put("magnetic_alignment", 0.97)
}
val receipt = Handshake.createReceipt(this, "DAO-COUNCIL-9", payload)
// receipt is now saved and signed forever