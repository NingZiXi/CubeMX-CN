import java.awt.*;
import java.awt.image.BufferedImage;
import java.nio.file.*;
import javax.imageio.ImageIO;
import javax.swing.*;
import cubemx.cn.bootstrap.Translator;

/** Run with the actual agent and runtime; compares rendered output to real Chinese controls. */
public final class RenderSmoke {
    static void require(boolean value, String reason) {
        if (!value) throw new AssertionError(reason);
    }
    static BufferedImage render(JComponent component) {
        component.setSize(240, 45);
        BufferedImage image = new BufferedImage(240, 45, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = image.createGraphics();
        g.setColor(Color.WHITE); g.fillRect(0, 0, 240, 45);
        component.paint(g); g.dispose();
        return image;
    }
    static void sameImage(BufferedImage a, BufferedImage b, String reason) {
        for (int x = 0; x < a.getWidth(); x++) for (int y = 0; y < a.getHeight(); y++)
            require(a.getRGB(x, y) == b.getRGB(x, y), reason + " at " + x + "," + y);
    }
    public static void main(String[] args) throws Exception {
        SwingUtilities.invokeAndWait(() -> {
            try {
                JLabel original = new JLabel("File");
                JLabel expected = new JLabel("文件");
                require(original.getPreferredSize().equals(expected.getPreferredSize()), "Chinese text measurement");
                sameImage(render(original), render(expected), "Chinese label pixels");
                require(original.getText().equals("File"), "Label model remains English");
                JLabel html = new JLabel("<html><b>File</b><br>Save</html>");
                sameImage(render(html), render(new JLabel("<html><b>文件</b><br>保存</html>")), "HTML label pixels");
                require(html.getText().equals("<html><b>File</b><br>Save</html>"), "HTML model preserved");
                require(Translator.translateHtml(original, "<html><a href='https://example.test/File?a=>'>File</a></html>")
                        .equals("<html><a href='https://example.test/File?a=>'>文件</a></html>"), "HTML attributes preserved");
                JButton button = new JButton("Save");
                button.addActionListener(event -> require(event.getActionCommand().equals("Save"), "Original action command"));
                button.doClick();
                sameImage(render(button), render(new JButton("保存")), "Chinese button pixels");
                JTextField input = new JTextField("File");
                require(Translator.translate(input, "File").equals("File"), "Editable text exclusion");
                require(Translator.translate(new JFileChooser(), "File").equals("File"), "File chooser exclusion");
                require(Translator.translate(original, "PA9").equals("PA9"), "Pin preserved");
                require(Translator.translate(original, "GPIO_MODE_OUTPUT_PP").equals("GPIO_MODE_OUTPUT_PP"), "Code token preserved");
                require(Translator.translate(original, " Save: ").equals(" 保存: "), "Padding and punctuation");
                require(Translator.translate(original, null) == null, "Null string");
                JMenuItem menu = new JMenuItem("File"); menu.setMnemonic('F');
                render(menu);
                require(menu.getMnemonic() == 'F', "Keyboard mnemonic preserved");
                Path output = Path.of(args[0]); Files.createDirectories(output.getParent());
                ImageIO.write(render(original), "png", output.toFile());
                System.out.println("PASS: rendering, HTML, layout, action commands, editing exclusions, pins, tokens, mnemonics");
            } catch (Exception e) { throw new RuntimeException(e); }
        });
    }
}
