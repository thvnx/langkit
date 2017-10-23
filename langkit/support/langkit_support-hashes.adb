with Interfaces;

package body Langkit_Support.Hashes is

   -------------
   -- Combine --
   -------------

   function Combine (L, R : Hash_Type) return Hash_Type is
      use Interfaces;

      --  The following is a translation from Boost's uint32_t hash function

      C1 : constant Unsigned_32 := 16#cc9e2d51#;
      C2 : constant Unsigned_32 := 16#1b873593#;
      H1 : Unsigned_32 := Unsigned_32 (L);
      K1 : Unsigned_32 := Unsigned_32 (R);
   begin
      K1 := K1 * C1;
      K1 := Rotate_Left (K1, 15);
      K1 := K1 * C2;

      H1 := H1 xor K1;
      H1 := Rotate_Left (H1, 13);
      H1 := H1 * 5 + 16#e6546b64#;

      return Hash_Type (H1);
   end Combine;

   -------------
   -- Combine --
   -------------

   function Combine (Hashes : Hash_Array) return Hash_Type is
      Result : Hash_Type := Initial_Hash;
   begin
      for H of Hashes loop
         Result := Combine (Result, H);
      end loop;
      return Result;
   end Combine;

end Langkit_Support.Hashes;