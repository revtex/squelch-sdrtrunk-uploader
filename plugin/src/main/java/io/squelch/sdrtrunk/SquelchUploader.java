// SPDX-License-Identifier: GPL-3.0-or-later
package io.squelch.sdrtrunk;

/**
 * Entry point for the Squelch SDRTrunk plugin.
 *
 * <p>Status: scaffolding. The class is wired up so the build produces a JAR
 * with a stable identity, but the SDRTrunk plugin SPI bindings are not yet
 * implemented. The Phase N-4 implementation will:
 *
 * <ul>
 *   <li>Subscribe to SDRTrunk's call-decoded events.
 *   <li>Build a multipart POST against {@code /api/v1/calls}.
 *   <li>Authenticate with {@code Authorization: Bearer <api-key>}.
 *   <li>Maintain a bounded worker queue with retry and backoff.
 * </ul>
 */
public final class SquelchUploader {

    public static final String PLUGIN_NAME = "squelch_uploader";
    public static final String PLUGIN_VERSION = "0.1.0";

    private SquelchUploader() {
        // Singleton — instantiated by SDRTrunk's plugin loader once SPI lands.
    }

    /**
     * Returns a human-readable plugin identity string. Used by tests and by
     * the eventual SPI registration code.
     *
     * @return plugin name and version, formatted as {@code name vversion}
     */
    public static String identity() {
        return PLUGIN_NAME + " v" + PLUGIN_VERSION;
    }
}
