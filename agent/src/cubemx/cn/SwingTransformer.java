package cubemx.cn;

import java.lang.instrument.ClassFileTransformer;
import java.security.ProtectionDomain;
import java.util.Set;
import jdk.internal.org.objectweb.asm.*;

final class SwingTransformer implements ClassFileTransformer {
    volatile int transformedMethods;
    private static final String HELPER = "cubemx/cn/bootstrap/Translator";
    private static final Set<String> METHODS = Set.of("stringWidth", "clipString", "clipStringIfNecessary",
            "drawString", "drawStringUnderlineCharAt");

    @Override
    public byte[] transform(Module module, ClassLoader loader, String name, Class<?> redefining,
                            ProtectionDomain domain, byte[] bytes) {
        boolean html = "javax/swing/plaf/basic/BasicHTML".equals(name);
        if (!html && !"sun/swing/SwingUtilities2".equals(name)) return null;
        try {
            ClassReader reader = new ClassReader(bytes);
            ClassWriter writer = new ClassWriter(reader, ClassWriter.COMPUTE_MAXS);
            reader.accept(new ClassVisitor(Opcodes.ASM8, writer) {
                @Override
                public MethodVisitor visitMethod(int access, String method, String descriptor,
                                                 String signature, String[] exceptions) {
                    MethodVisitor original = super.visitMethod(access, method, descriptor, signature, exceptions);
                    if (html) {
                        if (!method.equals("createHTMLView") || !descriptor.equals("(Ljavax/swing/JComponent;Ljava/lang/String;)Ljavax/swing/text/View;")) return original;
                        transformedMethods++;
                        return new MethodVisitor(Opcodes.ASM8, original) {
                            @Override public void visitCode() {
                                super.visitCode();
                                mv.visitVarInsn(Opcodes.ALOAD, 0);
                                mv.visitVarInsn(Opcodes.ALOAD, 1);
                                mv.visitMethodInsn(Opcodes.INVOKESTATIC, HELPER, "translateHtml",
                                        "(Ljavax/swing/JComponent;Ljava/lang/String;)Ljava/lang/String;", false);
                                mv.visitVarInsn(Opcodes.ASTORE, 1);
                            }
                            @Override public void visitMethodInsn(int opcode, String owner, String called, String desc, boolean itf) {
                                super.visitMethodInsn(opcode, owner, called, desc, itf);
                                if (called.equals("getFont") && desc.equals("()Ljava/awt/Font;")) {
                                    mv.visitMethodInsn(Opcodes.INVOKESTATIC, HELPER, "htmlFont", "(Ljava/awt/Font;)Ljava/awt/Font;", false);
                                }
                            }
                        };
                    }
                    if (!METHODS.contains(method) || !descriptor.startsWith("(Ljavax/swing/JComponent;")
                            || !descriptor.contains("Ljava/lang/String;")) return original;
                    transformedMethods++;
                    return new MethodVisitor(Opcodes.ASM8, original) {
                        @Override public void visitCode() {
                            super.visitCode();
                            // All selected methods have (JComponent, Graphics|FontMetrics, String, ...).
                            mv.visitVarInsn(Opcodes.ALOAD, 0);
                            mv.visitVarInsn(Opcodes.ALOAD, 2);
                            mv.visitMethodInsn(Opcodes.INVOKESTATIC, HELPER, "translate",
                                    "(Ljavax/swing/JComponent;Ljava/lang/String;)Ljava/lang/String;", false);
                            mv.visitVarInsn(Opcodes.ASTORE, 2);
                            if (descriptor.contains("Ljava/awt/FontMetrics;")) {
                                mv.visitVarInsn(Opcodes.ALOAD, 1);
                                mv.visitVarInsn(Opcodes.ALOAD, 2);
                                mv.visitMethodInsn(Opcodes.INVOKESTATIC, HELPER, "metrics",
                                        "(Ljava/awt/FontMetrics;Ljava/lang/String;)Ljava/awt/FontMetrics;", false);
                                mv.visitVarInsn(Opcodes.ASTORE, 1);
                            } else {
                                mv.visitVarInsn(Opcodes.ALOAD, 1);
                                mv.visitVarInsn(Opcodes.ALOAD, 2);
                                mv.visitMethodInsn(Opcodes.INVOKESTATIC, HELPER, "graphics",
                                        "(Ljava/awt/Graphics;Ljava/lang/String;)Ljava/awt/Graphics;", false);
                                mv.visitVarInsn(Opcodes.ASTORE, 1);
                                if (method.equals("drawStringUnderlineCharAt")) {
                                    mv.visitVarInsn(Opcodes.ALOAD, 2);
                                    mv.visitVarInsn(Opcodes.ILOAD, 3);
                                    mv.visitMethodInsn(Opcodes.INVOKESTATIC, HELPER, "mnemonic",
                                            "(Ljava/lang/String;I)I", false);
                                    mv.visitVarInsn(Opcodes.ISTORE, 3);
                                }
                            }
                        }
                        @Override public void visitInsn(int opcode) {
                            if (opcode == Opcodes.RETURN && descriptor.contains("Ljava/awt/Graphics;")) {
                                mv.visitVarInsn(Opcodes.ALOAD, 1);
                                mv.visitMethodInsn(Opcodes.INVOKEVIRTUAL, "java/awt/Graphics", "dispose",
                                        "()V", false);
                            }
                            super.visitInsn(opcode);
                        }
                    };
                }
            }, 0);
            return writer.toByteArray();
        } catch (Throwable error) {
            error.printStackTrace();
            transformedMethods = 0;
            return null;
        }
    }
}
