plugins {
    `java-library`
}

group = "io.squelch"
version = "0.1.0"
description = "Squelch uploader plugin for SDRTrunk"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
}

dependencies {
    // SDRTrunk's plugin SPI is not yet on Maven Central. Until it is, scaffold
    // builds against an empty dependency set; real implementation will pin a
    // specific SDRTrunk SPI version once published.

    testImplementation(platform("org.junit:junit-bom:5.10.2"))
    testImplementation("org.junit.jupiter:junit-jupiter")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.withType<JavaCompile> {
    options.compilerArgs.add("-Xlint:all")
    options.encoding = "UTF-8"
}

tasks.test {
    useJUnitPlatform()
    testLogging {
        events("passed", "failed", "skipped")
    }
}

tasks.jar {
    manifest {
        attributes(
            "Implementation-Title" to project.name,
            "Implementation-Version" to project.version,
            "Implementation-Vendor" to "Squelch maintainers",
        )
    }
}
