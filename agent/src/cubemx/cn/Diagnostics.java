package cubemx.cn;

import java.awt.*;
import java.awt.image.BufferedImage;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.ArrayList;
import javax.imageio.ImageIO;
import javax.swing.*;

/** Explicit developer-only screenshot of this JVM's own window, no desktop capture. */
final class Diagnostics {
    static void schedule() {
        Thread worker = new Thread(() -> {
            try {
                Thread.sleep(Long.getLong("cubemx.cn.captureDelay", 30000));
                SwingUtilities.invokeAndWait(() -> capture());
            } catch (Exception e) { e.printStackTrace(); }
        }, "CubeMX-CN-diagnostics");
        worker.setDaemon(true);
        worker.start();
    }

    private static void capture() {
        try {
            Path prefix = Path.of(System.getProperty("cubemx.cn.capture"));
            Files.createDirectories(prefix.getParent());
            int index = 0;
            for (Window window : Window.getWindows()) {
                if (!window.isShowing() || window.getWidth() < 200 || window.getHeight() < 150) continue;
                BufferedImage image = new BufferedImage(window.getWidth(), window.getHeight(), BufferedImage.TYPE_INT_RGB);
                Graphics2D g = image.createGraphics();
                window.paintAll(g);
                g.dispose();
                ImageIO.write(image, "png", Path.of(prefix + "-" + index + ".png").toFile());
                ArrayList<String> texts = new ArrayList<>();
                collect(window, texts);
                Files.write(Path.of(prefix + "-" + index + ".txt"), texts, StandardCharsets.UTF_8);
                index++;
            }
            System.err.println("[CubeMX-CN] Captured windows=" + index);
        } catch (Exception e) { e.printStackTrace(); }
    }

    private static void collect(Component c, ArrayList<String> texts) {
        String text = c instanceof JLabel label ? label.getText()
                : c instanceof AbstractButton button ? button.getText() : null;
        if (text != null && !text.isBlank()) texts.add(c.getClass().getName() + "\t" + text.replace('\n', ' '));
        if (c instanceof Container container) for (Component child : container.getComponents()) collect(child, texts);
    }
}
