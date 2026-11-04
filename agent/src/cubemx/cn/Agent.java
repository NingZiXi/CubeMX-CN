package cubemx.cn;

import java.lang.instrument.Instrumentation;
import java.nio.file.Path;
import java.util.Map;
import java.util.Set;
import java.util.jar.JarFile;

/** Optional process-local rendering agent; never rewrites the installed app. */
public final class Agent {
    private static JarFile bootstrapJar;

    public static void premain(String arguments, Instrumentation instrumentation) throws Exception {
        Path directory = Path.of(Agent.class.getProtectionDomain().getCodeSource().getLocation().toURI()).getParent();
        bootstrapJar = new JarFile(directory.resolve("cubemx-cn-bootstrap.jar").toFile());
        instrumentation.appendToBootstrapClassLoaderSearch(bootstrapJar);
        Class<?> translator = Class.forName("cubemx.cn.bootstrap.Translator", true, null);
        translator.getMethod("initialize").invoke(null);
        Module desktop = javax.swing.JComponent.class.getModule();
        instrumentation.redefineModule(desktop, Set.of(translator.getModule()), Map.of(), Map.of(), Set.of(), Map.of());
        instrumentation.redefineModule(Object.class.getModule(), Set.of(),
                Map.of("jdk.internal.org.objectweb.asm", Set.of(Agent.class.getModule())), Map.of(), Set.of(), Map.of());
        SwingTransformer transformer = new SwingTransformer();
        instrumentation.addTransformer(transformer, true);
        Class<?> swing = Class.forName("sun.swing.SwingUtilities2", false, null);
        instrumentation.retransformClasses(swing);
        instrumentation.retransformClasses(Class.forName("javax.swing.plaf.basic.BasicHTML", false, null));
        if (transformer.transformedMethods < 6) {
            throw new IllegalStateException("Unsupported Swing runtime: only " + transformer.transformedMethods + " hooks");
        }
        System.err.println("[CubeMX-CN] READY hooks=" + transformer.transformedMethods);
        if (System.getProperty("cubemx.cn.capture") != null) Diagnostics.schedule();
    }
}
