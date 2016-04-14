------------------------------------------------------------------------------
--                               A D A L O G                                --
--                                                                          --
--                     Copyright (C) 2016, AdaCore                          --
--                                                                          --
-- This library is free software;  you can redistribute it and/or modify it --
-- under terms of the  GNU General Public License  as published by the Free --
-- Software  Foundation;  either version 3,  or (at your  option) any later --
-- version. This library is distributed in the hope that it will be useful, --
-- but WITHOUT ANY WARRANTY;  without even the implied warranty of MERCHAN- --
-- TABILITY or FITNESS FOR A PARTICULAR PURPOSE.                            --
--                                                                          --
-- As a special exception under Section 7 of GPL version 3, you are granted --
-- additional permissions described in the GCC Runtime Library Exception,   --
-- version 3.1, as published by the Free Software Foundation.               --
--                                                                          --
-- You should have received a copy of the GNU General Public License and    --
-- a copy of the GCC Runtime Library Exception along with this program;     --
-- see the files COPYING3 and COPYING.RUNTIME respectively.  If not, see    --
-- <http://www.gnu.org/licenses/>.                                          --
--                                                                          --
------------------------------------------------------------------------------

with Adalog.Abstract_Relation; use Adalog.Abstract_Relation;
with Adalog.Logic_Var;
with Adalog.Relation_Interface;

package Adalog.Predicates is
   generic
      type El_Type is private;
      with package Var is new Logic_Var
        (Element_Type => El_Type, others => <>);
      with function Predicate (L : El_Type) return Boolean;
   package Predicate is
      type Predicate_Logic is record
         Ref : Var.Var;
      end record;

      function Call (Inst : in out Predicate_Logic) return Boolean;
      procedure Reset (Inst : in out Predicate_Logic);

      package Impl is new Relation_Interface (Ty => Predicate_Logic);

      function Create (R : Var.Var) return Predicate_Logic;
      function Create (R : Var.Var) return Rel
      is (Impl.Dynamic (Create (R)));

   end Predicate;

   generic
      type El_Type is private;
      with package Var is new Logic_Var
        (Element_Type => El_Type, others => <>);
   package Dyn_Predicate is

      type Predicate_Access is access function (L : El_Type) return Boolean;

      type Predicate_Logic is record
         Ref : Var.Var;
         P   : Predicate_Access;
      end record;

      function Call (Inst : in out Predicate_Logic) return Boolean;
      procedure Reset (Inst : in out Predicate_Logic);

      package Impl is new Relation_Interface (Ty => Predicate_Logic);

      function Create
        (R    : Var.Var;
         Pred : Predicate_Access)
         return Predicate_Logic;

      function Create
        (R    : Var.Var;
         Pred : Predicate_Access) return Rel
      is (Impl.Dynamic (Create (R, Pred)));
   end Dyn_Predicate;
end Adalog.Predicates;
