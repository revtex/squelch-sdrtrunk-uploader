// SPDX-License-Identifier: GPL-3.0-or-later
package io.squelch.sdrtrunk;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class SquelchUploaderTest {

    @Test
    void pluginNameIsStable() {
        assertEquals("squelch_uploader", SquelchUploader.PLUGIN_NAME);
    }

    @Test
    void identityIncludesVersion() {
        assertTrue(SquelchUploader.identity().contains(SquelchUploader.PLUGIN_VERSION));
    }
}
