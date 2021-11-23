## vim: filetype=makoada

with Langkit_Support.Generic_API; use Langkit_Support.Generic_API;

package ${ada_lib_name}.Generic_API is

   ${ctx.lang_name}_Lang_Id : constant Language_Id
     with Import, External_Name => "${ada_lib_name}__language_id";
   --  Unique identifier for ${ada_lib_name}

   Self_Id : Language_Id renames ${ctx.lang_name}_Lang_Id;
   --  Shortcut for convenience in code generation

private

   procedure Dummy;
   --  Dummy procedure so that this spec is allowed to have a body. See the
   --  body's hack to provide the Language_Id constant.

end ${ada_lib_name}.Generic_API;
