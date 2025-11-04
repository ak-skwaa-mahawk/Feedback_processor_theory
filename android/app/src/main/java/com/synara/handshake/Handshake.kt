package com.synara.handshake

import org.json.JSONObject
import java.security.MessageDigest
import java.io.File
import java.lang.System

object Handshake {
    fun sha256Hex(input: ByteArray): String {
        val md = MessageDigest.getInstance("SHA-256")
        val digest = md.digest(input)
        return digest.joinToString("") { String.format("%02x", it) }
    }

    fun createReceipt(nodeId: String, payload: JSONObject): JSONObject {
        val payloadBytes = payload.toString().toByteArray(Charsets.UTF_8)
        val hash = sha256Hex(payloadBytes)
        val receipt = JSONObject()
        receipt.put("node_id", nodeId)
        receipt.put("ts", System.currentTimeMillis() / 1000)
        receipt.put("payload_hash", hash)
        receipt.put("payload", payload)
        // write to app files dir or use ContentProvider
        return receipt
    }
}