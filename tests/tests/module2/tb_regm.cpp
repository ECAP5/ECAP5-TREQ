/*           __        _
 *  ________/ /  ___ _(_)__  ___
 * / __/ __/ _ \/ _ `/ / _ \/ -_)
 * \__/\__/_//_/\_,_/_/_//_/\__/
 * 
 * Copyright (C) Clément Chaine
 * This file is part of ECAP5-DPROC <https://github.com/cchaine/ECAP5-DPROC>
 *
 * ECAP5-DPROC is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * ECAP5-DPROC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with ECAP5-DPROC.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <verilated.h>
#include <verilated_vcd_c.h>
#include <svdpi.h>

#include "Vtb_regm.h"
#include "testbench.h"

class TB_Regm : public Testbench<Vtb_regm> {
public:
  void set_register(uint8_t addr, uint32_t value) {
    const svScope scope = svGetScopeFromName("TOP.tb_regm.dut");
    assert(scope);
    svSetScope(scope);
    this->core->set_register_value((svLogicVecVal*)&addr, (svLogicVecVal*)&value); 
  }
};

void tb_regm_read_port_a(TB_Regm * tb) {
  Vtb_regm * core = tb->core;
  bool success = true;
  for(int i = 0; i < 32; i++) {
    // set a random value inside the register to be read
    uint32_t value = rand();
    tb->set_register(i, value); 

    // set core inputs
    core->raddr1_i = i;
    core->write_i = 0;
    tb->tick();

    if(core->rdata1_o != value) {
      success = false;
    }
  }

  CHECK("tb_regm_read_port_a",
    success,
    "Failed to read registers from port A");

  // reset register x0
  tb->set_register(0, 0);
}

void tb_regm_read_port_b(TB_Regm * tb) {
  Vtb_regm * core = tb->core;
  bool success = true;
  for(int i = 0; i < 32; i++) {
    // set a random value inside the register to be read
    uint32_t value = rand();
    tb->set_register(i, value); 

    // set core inputs
    core->raddr2_i = i;
    core->write_i = 0;
    tb->tick();

    if(core->rdata2_o != value) {
      success = false;
    }
  }

  CHECK("tb_regm_read_port_b",
    success,
    "Failed to read registers from port B");

  // reset register x0
  tb->set_register(0, 0);
}

void tb_regm_write_x0(TB_Regm * tb) {
  Vtb_regm * core = tb->core;
  // write to x0
  core->waddr_i = 0;
  core->wdata_i = rand();
  core->write_i = 1;
  tb->tick();

  // read back x0
  core->raddr1_i = 0;
  core->write_i = 0;
  tb->tick();

  CHECK("tb_regm_write_x0",
    core->rdata1_o == 0,
    "Failed to prevent writing to x0");
}

void tb_regm_write(TB_Regm * tb) {
  Vtb_regm * core = tb->core;
  bool success = true;
  for(int i = 1; i < 32; i++) {
    // write a random value
    uint32_t value = rand();
    core->waddr_i = i;
    core->wdata_i = value;
    core->write_i = 1;
    tb->tick();

    // read back the register
    core->raddr1_i = i;
    core->write_i = 0;
    tb->tick();

    if(core->rdata1_o != value) {
      success = false;
    }
  }

  CHECK("tb_regm_write",
    success,
    "Failed writing to registers");
}

void tb_regm_parallel_read(TB_Regm * tb) {
  Vtb_regm * core = tb->core;
  // set a random value before reading back
  uint32_t value = rand();
  tb->set_register(5, value);

  // reading the same register from both ports
  core->raddr1_i = 5;
  core->raddr2_i = 5;
  core->write_i = 0;
  tb->tick();

  CHECK("tb_regm_parallel_read_01",
    core->rdata1_o == value,
    "Failed reading from port A");

  CHECK("tb_regm_parallel_read_02",
    core->rdata1_o == value,
    "Failed reading from port B");
}

void tb_regm_read_before_write(TB_Regm * tb) {
  Vtb_regm * core = tb->core;
  // write a value in the register
  uint32_t previous_value = rand();
  tb->set_register(5, previous_value);

  // read and write to the same register
  uint32_t value = rand();
  core->raddr1_i = 5;
  core->waddr_i = 5;
  core->wdata_i = value;
  core->write_i = 1;
  tb->tick();

  // check that the read result is the value set at the start
  CHECK("tb_regm_read_before_write_01",
    core->rdata1_o == previous_value,
    "Failed reading previous value");

  // read again
  core->write_i = 0;
  tb->tick();

  // check that the read result is the new written value
  CHECK("tb_regm_read_before_write_02",
    core->rdata1_o == value,
    "Failed reading the written value");
}

int main(int argc, char ** argv, char ** env) {
  srand(time(NULL));
  Verilated::traceEverOn(true);

  TB_Regm * tb = new TB_Regm;
  tb->open_trace("waves/regm.vcd");

  /************************************************************/

  tb_regm_read_port_a(tb);
  
  tb_regm_read_port_b(tb);

  tb_regm_write_x0(tb);

  tb_regm_write(tb);

  tb_regm_parallel_read(tb);

  tb_regm_read_before_write(tb);

  /************************************************************/

  printf("[REGM]: ");
  if(tb->success) {
    printf("Done\n");
  } else {
    printf("Failed\n");
  }

  delete tb;
  exit(EXIT_SUCCESS);
}
